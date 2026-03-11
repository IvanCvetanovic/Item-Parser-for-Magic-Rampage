import re
import logging
from pathlib import Path
from parser_utils import parse_scalar
from models import EnemyRecord

logger = logging.getLogger(__name__)

class EnemyParser:
    def __init__(self, directories):
        self.directories = directories

    def parse_character_block(self, block_text):
        enemy = {}
        depth = 0
        for raw_line in block_text.strip().splitlines():
            line = raw_line.split('//')[0].strip()
            if not line:
                continue
            if depth == 0 and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                parsed = parse_scalar(value.strip().strip('"'))
                enemy[key] = parsed
            depth += line.count('{')
            depth -= line.count('}')
        return enemy

    def extract_named_blocks(self, content, block_pattern):
        blocks = []
        pattern = re.compile(rf"\b(?:{block_pattern})\s*\{{", re.IGNORECASE)
        pos = 0

        while True:
            match = pattern.search(content, pos)
            if not match:
                break

            brace_start = content.find("{", match.start())
            depth = 1
            index = brace_start + 1
            while index < len(content) and depth > 0:
                char = content[index]
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                index += 1

            if depth == 0:
                blocks.append(content[brace_start + 1:index - 1])
            pos = index

        return blocks

    def parse_file(self, file_path):
        enemies = []
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        character_blocks = self.extract_named_blocks(content, r"character")

        for block in character_blocks:
            character = self.parse_character_block(block)
            item_stats = {"damage": 0, "armor": 0, "speedBoost": 1.0, "jumpImpulseBoost": 1.0}
            item_blocks = self.extract_named_blocks(block, r"equippedItem\d+")
            for item in item_blocks:
                parsed = self.parse_character_block(item)
                for key in item_stats:
                    val = parsed.get(key)
                    if val:
                        if key in ["speedBoost", "jumpImpulseBoost"]:
                            item_stats[key] *= val
                        else:
                            item_stats[key] += val
            character["_items"] = item_stats
            character["_filename"] = file_path.stem  # Store file name (stem only, no extension)
            enemies.append(character)
        return enemies

    def parse_enemy_data(self):
        all_enemies = []
        for directory in self.directories:
            if not Path(directory).exists():
                logger.debug("Enemy directory not found: %s", directory)
                continue
            for file in Path(directory).glob("*.character"):
                all_enemies.extend(self.parse_file(file))
        return [EnemyRecord.from_mapping(enemy) for enemy in all_enemies]

    def format_developer(self, enemy, name_counts):
        base = enemy.get("_filename", "unknown").lower().replace(" ", "_").replace("-", "_")
        name_counts[base] = name_counts.get(base, 0) + 1
        suffix = f"_{name_counts[base]}" if name_counts[base] > 1 else ""
        id_base = base + suffix

        health = int(enemy.get("resistance", 0))
        damage = int(enemy.get("_items", {}).get("damage", 0))
        damage_on_touch = int(enemy.get("passiveDamage", 0))
        armor = int(enemy.get("_items", {}).get("armor", 0))
        speed = round(float(enemy.get("speed", 0)) * float(enemy.get("_items", {}).get("speedBoost", 1.0)), 2)
        jump = round(float(enemy.get("jumpImpulse", 0)) * float(enemy.get("_items", {}).get("jumpImpulseBoost", 1.0)), 2)
        patrol = enemy.get("patrolBehaviour", "")
        attack = enemy.get("attackBehaviour", "")

        return (
            f'enemyList.add(new Enemy(str(context, R.string.enemy_{id_base}), {health}, '
            f'{damage}, {damage_on_touch}, {armor}, {speed}, {jump}, "{patrol}", "{attack}", '
            f'R.drawable.enemy_{id_base}));'
        )

    def format_normal(self, enemy):
        base = enemy.get("_filename", "unknown")
        name = base.replace("_", " ").replace("-", " ").title()
        health = enemy.get("resistance", 0)
        speed = round(float(enemy.get("speed", 0)) * float(enemy.get("_items", {}).get("speedBoost", 1.0)), 2)
        jump = round(float(enemy.get("jumpImpulse", 0)) * float(enemy.get("_items", {}).get("jumpImpulseBoost", 1.0)), 2)
        patrol = enemy.get("patrolBehaviour", "")
        attack = enemy.get("attackBehaviour", "")
        damage = int(enemy.get("_items", {}).get("damage", 0))
        armor = int(enemy.get("_items", {}).get("armor", 0))
        damage_on_touch = enemy.get("passiveDamage", 0)

        lines = [
            f"Name: {name}",
            f"Jump Impulse: {jump}",
            f"Speed: {speed}",
            f"Health (Resistance): {health}",
            f"Patrol Behaviour: {patrol}",
            f"Attack Behaviour: {attack}"
        ]
        if damage_on_touch:
            lines.append(f"Damage on Touch: {damage_on_touch}")
        if damage:
            lines.append(f"Damage (from items): {damage}")
        if armor:
            lines.append(f"Armor (from items): {armor}")

        return "\n".join(lines)

    def export_to_txt(self, enemies, output_path, mode="normal"):
        name_counts = {}
        sorted_enemies = sorted(enemies, key=lambda e: e.as_dict().get("resistance", 0) if hasattr(e, "as_dict") else e.get("resistance", 0))
        with open(output_path, "w", encoding="utf-8") as f:
            for enemy in sorted_enemies:
                if hasattr(enemy, "as_dict"):
                    enemy = enemy.as_dict()
                if mode == "developer":
                    f.write(self.format_developer(enemy, name_counts) + "\n")
                else:
                    f.write(self.format_normal(enemy) + "\n\n")

    def parse_enemy_stats(self, mode="normal"):
        enemies = self.parse_enemy_data()
        sorted_enemies = sorted(enemies, key=lambda e: e.as_dict().get("resistance", 0))
        lines = []
        name_counts = {}
        for enemy in sorted_enemies:
            enemy = enemy.as_dict()
            if mode == "developer":
                lines.append(self.format_developer(enemy, name_counts))
            else:
                lines.append(self.format_normal(enemy))
        return lines
