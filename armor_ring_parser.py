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
    return 0 if value == 0 or value == 1 else round((value - 1) * 100)

def generate_armor_code(data):

    armor_code_list = []

    if isinstance(data, list):
        data = sorted(data, key=lambda block: block.get("maxLevelArmor", 0))

        for block in data:
            if isinstance(block, dict) and block.get("type") == "armor":
                name = block.get("name_en", "test_armor").replace(" ", "_").replace("'", "").replace("+", "").replace("-", "").lower()
                frostImmune = block.get("frost", False)
                minArmor = block.get("armor", 0)
                maxArmor = block.get("maxLevelArmor", 0)
                upgrades = block.get("maxLevelAllowed", 1)

                if(upgrades == 0):
                    upgrades = 1

                speed = process_boost(block.get("speedBoost", 1))
                jump = process_boost(block.get("jumpBoost", 1))
                magic = process_boost(block.get("magicBoost", 1))
                sword = process_boost(block.get("swordBoost", 1))
                staff = process_boost(block.get("staffBoost", 1))
                dagger = process_boost(block.get("daggerBoost", 1))
                axe = process_boost(block.get("axeBoost", 1))
                hammer = process_boost(block.get("hammerBoost", 1))
                spear = process_boost(block.get("spearBoost", 1))

                element = block.get("element", "NEUTRAL").upper()
                if not element: 
                    element = "NEUTRAL"

                code = (
                    f"armorList.add(new Armor(str(context, R.string.{name}), Elements.{element}, "
                    f"{str(frostImmune).lower()}, {minArmor}, {maxArmor}, {upgrades}, "
                    f"{speed}, {jump}, {magic}, {sword}, "
                    f"{staff}, {dagger}, {axe}, {hammer}, "
                    f"{spear}, R.drawable.armor_{name}));"
                )
                armor_code_list.append(code)
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                armor_code_list.extend(generate_armor_code(value)) 

    return armor_code_list

def generate_ring_code(data):

    ring_code_list = []

    if isinstance(data, list):
        data = sorted(data, key=lambda block: block.get("maxLevelArmor", 0))

        for block in data:
            if isinstance(block, dict) and block.get("secondaryType") == "ring":

                name = block.get("name_en", "test_ring").replace(" ", "_").replace("'", "").replace("+", "").replace("-", "").lower()
                element = block.get("element", "NEUTRAL").upper()
                if not element:
                    element = "NEUTRAL"

                armor = block.get("maxLevelArmor", 0)

                armorBonus = process_boost(block.get("armorBoost", 1))

                speed = process_boost(block.get("speedBoost", 1))
                jump = process_boost(block.get("jumpBoost", 1))
                magic = process_boost(block.get("magicBoost", 1))
                sword = process_boost(block.get("swordBoost", 1))
                staff = process_boost(block.get("staffBoost", 1))
                dagger = process_boost(block.get("daggerBoost", 1))
                axe = process_boost(block.get("axeBoost", 1))
                hammer = process_boost(block.get("hammerBoost", 1))
                spear = process_boost(block.get("spearBoost", 1))

                code = (
                    f"ringList.add(new Ring(str(context, R.string.{name}), Elements.{element}, "
                    f"{armor}, {armorBonus}, "
                    f"{speed}, {jump}, {magic}, {sword}, "
                    f"{staff}, {dagger}, {axe}, {hammer}, "
                    f"{spear}, R.drawable.ring_{name}));"
                )
                ring_code_list.append(code)
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                ring_code_list.extend(generate_ring_code(value))

    return ring_code_list

