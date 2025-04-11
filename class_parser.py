# class_parser.py
import os
import math

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
                    print(f"[DEBUG] Malformed line in class block: {e}")
                    continue
                item[key.strip()] = value.strip().rstrip(";")
        return item

    def parse_file(self):
        if not os.path.exists(self.file_path):
            print(f"[DEBUG] File {self.file_path} not found.")
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        blocks = []
        block_lines = []
        inside_block = False
        pending_item = False
        current_identifier = ""
        for line in lines:
            line_stripped = line.strip()

            if not line_stripped or line_stripped.startswith("//"):
                continue

            if (line_stripped.startswith("helmet") or 
                line_stripped.startswith("hood") or 
                line_stripped.startswith("hat")):
                pending_item = True
                current_identifier = line_stripped
                continue

            if pending_item and "{" in line_stripped:
                inside_block = True
                pending_item = False
                block_lines = [line_stripped[line_stripped.index("{") + 1:]]
                continue

            if inside_block:
                if "}" in line_stripped:
                    inside_block = False
                    block_text = "\n".join(block_lines)
                    block = self.parse_class_block(block_text)
                    block["identifier"] = current_identifier
                    blocks.append(block)
                    block_lines = []
                    continue
                block_lines.append(line_stripped)
        print(f"[DEBUG] Total class blocks parsed: {len(blocks)}")
        return blocks

    def compute_parameters(self, block):
        """
        Dynamically compute the 10 parameters for CharacterClass.
        This example formula computes each boost parameter as floor((boost - 1)*100).
        Adjust the formulas as needed.
        """
        def calc(field):
            try:
                val = float(block.get(field, "1"))
                return math.floor((val - 1) * 100)
            except:
                return 0

        p1 = 0
        p2 = 0
        p3 = calc("swordBoost")
        p4 = calc("daggerBoost")
        p5 = calc("hammerBoost")
        p6 = calc("axeBoost")
        p7 = 0
        p8 = 0
        p9 = calc("speedBoost")
        p10 = calc("jumpBoost")
        return (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10)

    def generate_class_code(self):
        blocks = self.parse_file()
        code_lines = []
        for block in blocks:
            cls = block.get("class", "").strip().lower()
            if not cls:
                print(f"[DEBUG] Block with identifier '{block.get('identifier', '')}' has no 'class' field.")
                continue
            params = self.compute_parameters(block)
            enum_name = cls.upper().replace("-", "_")
            drawable = f"R.drawable.class_{cls.replace('-', '_')}"
            code_line = (
                f"classList.add(new CharacterClass(ClassNames.{enum_name}, "
                f"{params[0]}, {params[1]}, {params[2]}, {params[3]}, {params[4]}, "
                f"{params[5]}, {params[6]}, {params[7]}, {params[8]}, {params[9]}, {drawable}));"
            )
            code_lines.append(code_line)
        return code_lines

    def format_class_human(self):
        blocks = self.parse_file()
        lines = []
        for block in blocks:
            cls_val = block.get("class", "").strip().lower()
            if not cls_val:
                continue

            def calc_field(field):
                try:
                    val = float(block.get(field, "1"))
                    return int((val - 1) * 100)
                except:
                    return 0

            armorBonus = calc_field("armorBoost")
            magicBonus = calc_field("magicBoost")
            swordBonus = calc_field("swordBoost")
            daggerBonus = calc_field("daggerBoost")
            hammerBonus = calc_field("hammerBoost")
            axeBonus = calc_field("axeBoost")
            spearBonus = calc_field("spearBoost")
            staffBonus = calc_field("staffBoost")
            speedBonus = calc_field("speedBoost")
            jumpImpulseBonus = calc_field("jumpBoost")

            # Construct a summary line for the class
            line = (f"Class: {cls_val.title()}, Armor Bonus: {armorBonus}%, Magic Bonus: {magicBonus}%, "
                    f"Sword Bonus: {swordBonus}%, Dagger Bonus: {daggerBonus}%, Hammer Bonus: {hammerBonus}%, "
                    f"Axe Bonus: {axeBonus}%, Spear Bonus: {spearBonus}%, Staff Bonus: {staffBonus}%, "
                    f"Speed Bonus: {speedBonus}%, Jump Impulse Bonus: {jumpImpulseBonus}%")
            lines.append(line)
        return lines

