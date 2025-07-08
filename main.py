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
    code_lines = (cp.generate_class_code()
                  if output_type == "developer"
                  else cp.format_class_human())
    os.makedirs("output", exist_ok=True)
    out = os.path.join("output", "class_code.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(code_lines))
    print(f"[✓] Class list exported to: {out}")

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
        formatted = "\n".join(codes)

    else:  # normal
        if mode == "armor":
            formatted = OutputFormatter.format_human_armor(data.get(mode, []))
        elif mode in ["sword", "hammer", "spear", "staff", "dagger", "axe"]:
            formatted = OutputFormatter.format_human_weapon(data.get(mode, []))
        elif mode == "ring":
            formatted = OutputFormatter.format_human_ring(data.get(mode, []))
        else:
            formatted = ""

    os.makedirs("output", exist_ok=True)
    out = os.path.join("output", f"{mode}_code.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write(formatted)
    print(f"[✓] {mode.capitalize()} exported to: {out}")

def handle_all_types(data, output_type):
    for t in data:
        save_output(data, t, output_type)

def main():
    p = argparse.ArgumentParser("Parse Magic Rampage ENML files")
    p.add_argument("output_type", choices=["developer","normal"],
                   nargs="?", default="normal")
    p.add_argument("item_type", choices=[
        "armor","ring","sword","hammer","spear","staff","dagger","axe",
        "all","class","enemy"
    ], nargs="?", default="all")
    args = p.parse_args()

    folder = r"C:\Program Files (x86)\Steam\steamapps\common\Magic Rampage\items"

    # parse or fallback to online
    file_map = {
        "special-armors.enml": "armor", "armor-cloth-1.enml": "armor",
        "armor-leather-1.enml": "armor", "armor-plate-1.enml": "armor",
        "special-items.enml": "ring", "special-swords.enml": "sword",
        "weapon-sword-1.enml": "sword", "special-spears.enml": "spear",
        "special-staves.enml": "staff", "weapon-staff-1.enml": "staff",
        "special-hammers.enml": "hammer", "special-daggers.enml": "dagger",
        "special-shurikens.enml": "dagger", "weapon-dagger-1.enml": "dagger",
        "special-grimoires.enml": "staff", "special-axes.enml": "axe",
        "weapon-axe-1.enml": "axe", "weapon-axe-2.enml": "axe"
    }
    local = FileParser(folder, file_map).parse_files()
    total = sum(len(v) for v in local.values())

    if total == 0:
        print("[DEBUG] No local items, fetching online fallback")
    online_url = "https://gist.githubusercontent.com/andresan87/.../raw"
    od = OnlineDataManager()
    online = od.get_online_item_data(online_url)
    if online:
        merged = (od.convert_online_to_local(online)
                  if total==0
                  else od.merge_online_fields(local, od.index_online_data(online)))
    else:
        merged = local

    merged = DataFilter().filter_parsed_data(merged)

    # ─── Reclassify maces & hammers from axe → hammer ──────────────
    axe_blocks = merged.get("axe", [])
    # pick out any block whose secondaryType is "mace" or "hammer"
    to_move = [
        b for b in axe_blocks
        if b.get("secondaryType", "").lower() in ("mace", "hammer")
    ]
    if to_move:
        # leave only true axes behind
        merged["axe"]    = [b for b in axe_blocks if b not in to_move]
        # append both maces and hammers onto your hammer list
        merged["hammer"] = merged.get("hammer", []) + to_move
    # ────────────────────────────────────────────────────────────────

    if args.item_type == "class":
        process_class_file(folder, args.output_type)
    elif args.item_type == "enemy":
        dirs = [
            r"C:\Program Files (x86)\Steam\steamapps\common\Magic Rampage\npcs\enemies",
            r"C:\Program Files (x86)\Steam\steamapps\common\Magic Rampage\npcs\bosses"
        ]
        names = EnemyParser(dirs).parse_enemy_stats()
        os.makedirs("output", exist_ok=True)
        out = os.path.join("output","enemy_code.txt")
        with open(out,"w",encoding="utf-8") as f:
            f.write("\n".join(names))
        print(f"[✓] Enemy list exported to: {out}")
    else:
        if args.item_type == "all":
            handle_all_types(merged, args.output_type)
            process_class_file(folder, args.output_type)
        else:
            save_output(merged, args.item_type, args.output_type)

if __name__ == "__main__":
    main()
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
