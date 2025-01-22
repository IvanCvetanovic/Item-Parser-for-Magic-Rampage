import os
import argparse
from armor_ring_parser import fetch_json_from_url, generate_armor_code, generate_ring_code
from weapon_parser import (
    generate_sword_code,
    generate_hammer_code,
    generate_spear_code,
    generate_staff_code,
    generate_dagger_code,
    generate_axe_code,
)

def format_output_developer(codes):
    """Format output for developer mode (raw code)."""
    return "\n".join(codes)

def format_output_normal(codes):
    formatted = []
    
    for code in codes:
        if "createRing" in code:
            start = code.index("createRing(") + len("createRing(")
            end = code.rindex(")")
            arguments = code[start:end].split(", ")
            arguments = [arg.strip() for arg in arguments]

            if len(arguments) == 14:
                name = arguments[0].replace("R.string.", "").replace("_", " ").title()
                element = arguments[1].replace("Elements.", "").title()
                armor = arguments[2]
                bonus_armor = arguments[3]
                speed = arguments[5]
                jump = arguments[6]
                magic = arguments[7]
                sword = arguments[8]
                staff = arguments[9]
                dagger = arguments[10]
                axe = arguments[11]
                hammer = arguments[12]
                spear = arguments[13]

                formatted.append(
                    f"Item Name: {name}, Element: {element}, Armor: {armor}, Bonus Armor: {bonus_armor}, "
                    f"Speed: {speed}, Jump: {jump}, Magic: {magic}, Sword Bonus: {sword}, "
                    f"Staff Bonus: {staff}, Dagger Bonus: {dagger}, Axe Bonus: {axe}, "
                    f"Hammer Bonus: {hammer}, Spear Bonus: {spear}"
                )
            
        elif "createArmor" in code:
            start = code.index("createArmor(") + len("createArmor(")
            end = code.rindex(")")
            arguments = code[start:end].split(", ")
            arguments = [arg.strip() for arg in arguments]

            if len(arguments) == 16:
                name = arguments[0].replace("R.string.", "").replace("_", " ").title()
                element = arguments[1].replace("Elements.", "").title()
                frost_immune = arguments[2]
                min_armor = arguments[3]
                max_armor = arguments[4]
                upgrades = arguments[5]
                speed = arguments[6]
                jump = arguments[7]
                magic = arguments[8]
                sword = arguments[9]
                staff = arguments[10]
                dagger = arguments[11]
                axe = arguments[12]
                hammer = arguments[13]
                spear = arguments[14]

                formatted.append(
                    f"Item Name: {name}, Element: {element}, Frost Immune: {frost_immune}, "
                    f"Minimum Armor: {min_armor}, Maximum Armor: {max_armor}, Upgrades: {upgrades}, "
                    f"Speed: {speed}, Jump: {jump}, Magic: {magic}, Sword Bonus: {sword}, "
                    f"Staff Bonus: {staff}, Dagger Bonus: {dagger}, Axe Bonus: {axe}, "
                    f"Hammer Bonus: {hammer}, Spear Bonus: {spear}"
                )
            
        elif "createWeapon" in code:
            start = code.index("createWeapon(") + len("createWeapon(")
            end = code.rindex(")")
            arguments = code[start:end].split(", ")
            arguments = [arg.strip() for arg in arguments]

            if len(arguments) == 9:
                name = arguments[0].replace("R.string.", "").replace("_", " ").title()
                element = arguments[1].replace("Elements.", "").title()
                min_damage = arguments[2]
                max_damage = arguments[3]
                upgrades = arguments[4]
                armor_bonus = arguments[5]
                speed = arguments[6]
                jump = arguments[7]

                formatted.append(
                    f"Item Name: {name}, Element: {element}, Minimum Damage: {min_damage}, "
                    f"Maximum Damage: {max_damage}, Upgrades: {upgrades}, Armor Bonus: {armor_bonus}, "
                    f"Speed: {speed}, Jump: {jump}"
                )
            
    return "\n".join(formatted)

def process_data(data, mode):
    """Process data based on the mode."""
    if mode == "armor":
        return generate_armor_code(data)
    elif mode == "ring":
        return generate_ring_code(data)
    elif mode == "sword":
        return generate_sword_code(data)
    elif mode == "hammer":
        return generate_hammer_code(data)
    elif mode == "spear":
        return generate_spear_code(data)
    elif mode == "staff":
        return generate_staff_code(data)
    elif mode == "dagger":
        return generate_dagger_code(data)
    elif mode == "axe":
        return generate_axe_code(data)
    else:
        raise ValueError(f"Invalid mode: {mode}")

def save_output(data, mode, output_type):
    """Generate and save output for the given mode and output type."""
    codes = process_data(data, mode)
    if output_type == "developer":
        formatted_output = format_output_developer(codes)
    elif output_type == "normal":
        formatted_output = format_output_normal(codes)
    else:
        raise ValueError(f"Invalid output type: {output_type}")

    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)
    
    output_file = os.path.join(output_folder, f"{mode}_code.txt")
    with open(output_file, "w") as file:
        file.write(formatted_output)
    print(f"{mode.capitalize()} code has been exported to {output_file}")

def handle_all_types(data, output_type):
    """Process and save output for all item types separately."""
    item_types = ["armor", "ring", "sword", "hammer", "spear", "staff", "dagger", "axe"]
    for item_type in item_types:
        save_output(data, item_type, output_type)

def main():
    url = "https://gist.githubusercontent.com/andresan87/5670c559e5a930129aa03dfce7827306/raw"
    json_data = fetch_json_from_url(url)

    if json_data is not None:
        parser = argparse.ArgumentParser(description="Parse items for Magic Rampage.")
        
        parser.add_argument(
            "output_type",
            type=str,
            choices=["developer", "normal"],
            help="Specify the output type (developer or normal).",
            default="normal",
            nargs="?" 
        )
        
        parser.add_argument(
            "item_type",
            type=str,
            choices=["armor", "ring", "sword", "hammer", "spear", "staff", "dagger", "axe", "all"],
            help="Specify the item type (armor, ring, sword, etc. or all).",
            default="all",
            nargs="?"
        )
        
        args = parser.parse_args()

        if args.item_type == "all":
            if args.output_type == "developer":
                handle_all_types(json_data, "developer")
            else:
                handle_all_types(json_data, "normal")
        else:
            save_output(json_data, args.item_type, args.output_type)

    else:
        print("Failed to fetch data. Please check the URL.")

if __name__ == "__main__":
    main()
