import logging
from pathlib import Path
from armor_ring_parser import generate_armor_code, generate_ring_code
from weapon_parser import (
    generate_axe_code,
    generate_dagger_code,
    generate_hammer_code,
    generate_spear_code,
    generate_staff_code,
    generate_sword_code,
)
from class_parser import ClassParser
from enemy_parser import EnemyParser
from formatter import OutputFormatter

logger = logging.getLogger(__name__)

WEAPON_GENERATORS = {
    "sword": generate_sword_code,
    "hammer": generate_hammer_code,
    "spear": generate_spear_code,
    "staff": generate_staff_code,
    "dagger": generate_dagger_code,
    "axe": generate_axe_code,
}


class ExportService:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)

    def write_text(self, filename, content):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        out = self.output_dir / filename
        out.write_text(content, encoding="utf-8")
        logger.info("Exported %s", out)
        return out

    def export_items(self, items_by_type, item_type, output_type):
        items = items_by_type.get(item_type, [])
        if output_type == "developer":
            content = self._format_developer_items(item_type, items)
        else:
            content = self._format_normal_items(item_type, items)
        return self.write_text(f"{item_type}_code.txt", content)

    def export_all_items(self, items_by_type, output_type):
        outputs = []
        for item_type, items in items_by_type.items():
            if not items:
                continue
            outputs.append(self.export_items(items_by_type, item_type, output_type))
        return outputs

    def export_classes(self, items_folder, output_type):
        class_file = Path(items_folder) / "class-heads.enml"
        parser = ClassParser(str(class_file))
        lines = parser.generate_class_code() if output_type == "developer" else parser.format_class_human()
        return self.write_text("class_code.txt", "\n".join(lines))

    def export_enemies(self, enemy_directories, output_type):
        parser = EnemyParser([str(path) for path in enemy_directories])
        lines = parser.parse_enemy_stats(mode=output_type)
        return self.write_text("enemy_code.txt", "\n".join(lines))

    @staticmethod
    def _format_developer_items(item_type, items):
        if item_type == "armor":
            return "\n".join(generate_armor_code(items))
        if item_type == "ring":
            return "\n".join(generate_ring_code(items))
        if item_type in WEAPON_GENERATORS:
            return "\n".join(WEAPON_GENERATORS[item_type](items))
        return ""

    @staticmethod
    def _format_normal_items(item_type, items):
        if item_type == "armor":
            return OutputFormatter.format_human_armor(items)
        if item_type == "ring":
            return OutputFormatter.format_human_ring(items)
        if item_type in WEAPON_GENERATORS:
            return OutputFormatter.format_human_weapon(items, default_weapon_type=item_type)
        return ""
