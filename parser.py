import json
import requests

def fetch_json_from_url(url):

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def process_boost(value):
    return 0 if value == 1 else int((value - 1) * 100)

def clean_name(name):
    if name:
        name = name.replace("'", "")
        name = name.replace("+", "_plus")
    return name

def generate_armor_code(data):

    armor_code_list = []

    if isinstance(data, list):
        for block in data:
            if isinstance(block, dict) and block.get("type") == "armor":
 
                name = block.get("name", "test_armor").replace(" ", "_").lower()
                frost = block.get("frost", False)
                min_armor = block.get("armor", 0)
                max_armor = block.get("maxLevelArmor", 0)
                upgrades = block.get("maxLevelAllowed", 0)

                speed_boost = process_boost(block.get("speedBoost", 1))
                jump_boost = process_boost(block.get("jumpBoost", 1))
                magic_boost = process_boost(block.get("magicBoost", 1))
                sword_boost = process_boost(block.get("swordBoost", 1))
                staff_boost = process_boost(block.get("staffBoost", 1))
                dagger_boost = process_boost(block.get("daggerBoost", 1))
                axe_boost = process_boost(block.get("axeBoost", 1))
                hammer_boost = process_boost(block.get("hammerBoost", 1))
                spear_boost = process_boost(block.get("spearBoost", 1))

                # Parse the element from the block
                element = block.get("element", "NEUTRAL").upper()  # Default to "NEUTRAL" if not found

                code = (
                    f"armorList.add(createArmor(R.string.{name}, Elements.{element}, "
                    f"{str(frost).lower()}, {min_armor}, {max_armor}, {upgrades}, "
                    f"{speed_boost}, {jump_boost}, {magic_boost}, {sword_boost}, "
                    f"{staff_boost}, {dagger_boost}, {axe_boost}, {hammer_boost}, "
                    f"{spear_boost}, R.drawable.armor_{name}));"
                )
                armor_code_list.append(code)
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                armor_code_list.extend(generate_armor_code(value))  # Recursive call

    return armor_code_list

