import os
import logging
from parser_utils import parse_scalar, process_boost
from models import ClassRecord

logger = logging.getLogger(__name__)

class ClassParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse_class_block(self, block_text):
        item = {}
        for line in block_text.strip().splitlines():
            if '//' in line:
                line = line.split('//')[0]
            line = line.strip()
            if "=" in line:
                try:
                    key, value = line.split("=", 1)
                except Exception as e:
                    logger.debug("Malformed line in class block: %s", e)
                    continue
                item[key.strip()] = parse_scalar(value)
        return item

    def parse_file(self):
        if not os.path.exists(self.file_path):
            logger.debug("Class file not found: %s", self.file_path)
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        blocks = []
        block_lines = []
        inside_block = False
        pending_item = False
        current_identifier = ""
        for line in lines:
            s = line.strip()
            # skip blank or comment
            if not s or s.startswith("//"):
                continue

            # start of a class block
            if s.startswith(("helmet","hood","hat")):
                pending_item = True
                current_identifier = s
                continue

            if pending_item and "{" in s:
                inside_block = True
                pending_item = False
                block_lines = [s.split("{",1)[1]]
                continue

            if inside_block:
                if "}" in s:
                    inside_block = False
                    block_text = "\n".join(block_lines)
                    block = self.parse_class_block(block_text)
                    block["identifier"] = current_identifier
                    blocks.append(ClassRecord.from_mapping(block))
                    block_lines = []
                    continue
                block_lines.append(s)

        logger.info("Parsed %s class block(s)", len(blocks))
        return blocks

    def compute_parameters(self, block):
        # order must match your CharacterClass ctor:
        # armor, magic, sword, dagger, hammer, axe, spear, staff, speed, jump
        p1 = process_boost(block.get("armorBoost", 1))
        p2 = process_boost(block.get("magicBoost", 1))
        p3 = process_boost(block.get("swordBoost", 1))
        p4 = process_boost(block.get("daggerBoost", 1))
        p5 = process_boost(block.get("hammerBoost", 1))
        p6 = process_boost(block.get("axeBoost", 1))
        p7 = process_boost(block.get("spearBoost", 1))
        p8 = process_boost(block.get("staffBoost", 1))
        p9 = process_boost(block.get("speedBoost", 1))
        p10 = process_boost(block.get("jumpBoost", 1))

        return (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10)

    def generate_class_code(self):
        blocks = self.parse_file()
        code_lines = []
        for block in blocks:
            block = block.as_dict()
            cls = block.get("class", "").strip().lower()
            if not cls:
                logger.debug("Class block %s has no class field", block.get("identifier", ""))
                continue
            params = self.compute_parameters(block)
            enum_name = cls.upper().replace("-", "_")
            drawable  = f"R.drawable.class_{cls.replace('-', '_')}"
            line = (
                f"classList.add(new CharacterClass(ClassNames.{enum_name}, "
                f"{params[0]}, {params[1]}, {params[2]}, {params[3]}, {params[4]}, "
                f"{params[5]}, {params[6]}, {params[7]}, {params[8]}, {params[9]}, {drawable}));"
            )
            code_lines.append(line)
        return code_lines

    def format_class_human(self):
        blocks = self.parse_file()
        lines = []
        for block in blocks:
            block = block.as_dict()
            cls_val = block.get("class", "").strip().lower()
            if not cls_val:
                continue

            armorBonus = process_boost(block.get("armorBoost", 1))
            magicBonus = process_boost(block.get("magicBoost", 1))
            swordBonus = process_boost(block.get("swordBoost", 1))
            daggerBonus = process_boost(block.get("daggerBoost", 1))
            hammerBonus = process_boost(block.get("hammerBoost", 1))
            axeBonus = process_boost(block.get("axeBoost", 1))
            spearBonus = process_boost(block.get("spearBoost", 1))
            staffBonus = process_boost(block.get("staffBoost", 1))
            speedBonus = process_boost(block.get("speedBoost", 1))
            jumpImpulseBonus = process_boost(block.get("jumpBoost", 1))

            line = (
                f"Class: {cls_val.title()}, Armor Bonus: {armorBonus}%, Magic Bonus: {magicBonus}%, "
                f"Sword Bonus: {swordBonus}%, Dagger Bonus: {daggerBonus}%, Hammer Bonus: {hammerBonus}%, "
                f"Axe Bonus: {axeBonus}%, Spear Bonus: {spearBonus}%, Staff Bonus: {staffBonus}%, "
                f"Speed Bonus: {speedBonus}%, Jump Impulse Bonus: {jumpImpulseBonus}%"
            )
            lines.append(line)
        return lines
