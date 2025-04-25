import os
import argparse
from file_parser import FileParser
from online_data import OnlineDataManager
from filter_util import DataFilter
from formatter import OutputFormatter
from armor_ring_parser import generate_armor_code, generate_ring_code
from weapon_parser import (
    generate_sword_code, generate_hammer_code, generate_spear_code,
    generate_staff_code, generate_dagger_code, generate_axe_code
)
from class_parser import ClassParser
from enemy_parser import EnemyParser

def process_class_file(folder_path, output_type):
    class_file = os.path.join(folder_path, "class-heads.enml")
    cp = ClassParser(class_file)
    if output_type == "developer":
        code_lines = cp.generate_class_code()
    else:
        code_lines = cp.format_class_human()
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, "class_code.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(code_lines))
    print(f"[✓] Class list exported to: {output_file}")

def save_output(data, mode, output_type):
    if output_type == "developer":
        if mode == "armor":
            codes = generate_armor_code(data.get(mode, []))
        elif mode == "ring":
            codes = generate_ring_code(data.get(mode, []))
        elif mode == "sword":
            codes = generate_sword_code(data.get(mode, []))
        elif mode == "hammer":
            codes = generate_hammer_code(data.get(mode, []))
        elif mode == "spear":
            codes = generate_spear_code(data.get(mode, []))
        elif mode == "staff":
            codes = generate_staff_code(data.get(mode, []))
        elif mode == "dagger":
            codes = generate_dagger_code(data.get(mode, []))
        elif mode == "axe":
            codes = generate_axe_code(data.get(mode, []))
        else:
            codes = []
        formatted_output = "\n".join(codes)
    elif output_type == "normal":
        if mode == "armor":
            formatted_output = OutputFormatter.format_human_armor(data.get(mode, []))
        elif mode in ["sword", "hammer", "spear", "staff", "dagger", "axe"]:
            formatted_output = OutputFormatter.format_human_weapon(data.get(mode, []))
        elif mode == "ring":
            formatted_output = OutputFormatter.format_human_ring(data.get(mode, []))
        else:
            formatted_output = ""
    else:
        raise ValueError("Invalid output type")
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"{mode}_code.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(formatted_output)
    print(f"[✓] {mode.capitalize()} exported to: {output_file}")

def handle_all_types(data, output_type):
    for item_type in data.keys():
        save_output(data, item_type, output_type)

def main():
    parser = argparse.ArgumentParser(description="Parse Magic Rampage ENML files")
    parser.add_argument("output_type", type=str, choices=["developer", "normal"],
                        help="Choose output format", default="normal", nargs="?")
    parser.add_argument("item_type", type=str,
                        choices=["armor", "ring", "sword", "hammer", "spear", "staff", "dagger", "axe", "all", "class", "enemy"],
                        help="Choose item type", default="all", nargs="?")
    args = parser.parse_args()

    folder_path = r"C:\Program Files (x86)\Steam\steamapps\common\Magic Rampage\items"

    if args.item_type == "class":
        process_class_file(folder_path, args.output_type)
    elif args.item_type == "enemy":
        enemy_dirs = [
            r"C:\Program Files (x86)\Steam\steamapps\common\Magic Rampage\npcs\enemies",
            r"C:\Program Files (x86)\Steam\steamapps\common\Magic Rampage\npcs\bosses"
        ]
        parser = EnemyParser(enemy_dirs)
        names = parser.parse_enemy_stats()
        output_folder = "output"
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, "enemy_code.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(names))
        print(f"[✓] Enemy list exported to: {output_file}")
    else:
        # Build a file mapping that includes additional files for armors and weapons.
        file_mapping = {
            "special-armors.enml": "armor",
            "armor-cloth-1.enml": "armor",
            "armor-leather-1.enml": "armor",
            "armor-plate-1.enml": "armor",
            "special-items.enml": "ring",
            "special-swords.enml": "sword",
            "weapon-sword-1.enml": "sword",
            "special-spears.enml": "spear",
            "special-staves.enml": "staff",
            "weapon-staff-1.enml": "staff",
            "special-hammers.enml": "hammer",
            "special-daggers.enml": "dagger",
            "special-shurikens.enml": "dagger",
            "weapon-dagger-1.enml": "dagger",
            "special-grimoires.enml": "staff",
            "special-axes.enml": "axe",
            "weapon-axe-1.enml": "axe",
            "weapon-axe-2.enml": "axe"
        }
        file_parser = FileParser(folder_path, file_mapping)
        local_data = file_parser.parse_files()
        total_items = sum(len(lst) for lst in local_data.values())
        if total_items == 0:
            print("[DEBUG] Local directory exists but no items were parsed, falling back to online data.")

        online_url = "https://gist.githubusercontent.com/andresan87/5670c559e5a930129aa03dfce7827306/raw"
        online_manager = OnlineDataManager()
        online_data = online_manager.get_online_item_data(online_url)
        if online_data:
            if total_items == 0:
                merged_data = online_manager.convert_online_to_local(online_data)
            else:
                online_index = online_manager.index_online_data(online_data)
                merged_data = online_manager.merge_online_fields(local_data, online_index)
        else:
            merged_data = local_data

        filterer = DataFilter()
        merged_data = filterer.filter_parsed_data(merged_data)

        if args.item_type == "all":
            handle_all_types(merged_data, args.output_type)
            process_class_file(folder_path, args.output_type)
        else:
            save_output(merged_data, args.item_type, args.output_type)

if __name__ == "__main__":
    import sys
    output_type = "normal"
    if len(sys.argv) > 1 and sys.argv[1] in ("normal", "developer"):
        output_type = sys.argv[1]

    parser = EnemyParser([
        r"C:\Program Files (x86)\Steam\steamapps\common\Magic Rampage\npcs\enemies",
        r"C:\Program Files (x86)\Steam\steamapps\common\Magic Rampage\npcs\bosses"
    ])
    lines = parser.parse_enemy_stats(mode=output_type)

    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, "enemy_code.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n\n".join(lines) if output_type == "normal" else "\n".join(lines))
    print(f"[✓] Enemy list exported to: {output_file}")
