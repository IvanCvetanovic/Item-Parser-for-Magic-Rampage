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

def sort_by_max_damage(weapon_list):
    return sorted(weapon_list, key=lambda x: x['maxDamage'])

def extract_common_fields(block, default_name, weapon_type):
    name = block.get("name", default_name).replace(" ", "_").replace("'", "").replace("+", "").replace("-", "").lower()
    element = block.get("element", "NEUTRAL").upper()
    if not element:
        element = "NEUTRAL"
    minDamage = block.get("damage", 0)
    maxDamage = block.get("maxLevelDamage", 0)
    upgrades = block.get("maxLevelAllowed", 0)
    if upgrades == 0:
        upgrades = 1
    armorBonus = process_boost(block.get("armorBoost", 1))
    speed = process_boost(block.get("speedBoost", 1))
    jump = process_boost(block.get("jumpBoost", 1))
    attackCooldown = block.get("attackCooldown", 0)
    pierceCount = block.get("pierceCount", 0)
    enablePierceAreaDamage = block.get("enablePierceAreaDamage", False)
    persistAgainstProjectile = block.get("persistAgainstProjectile", False)
    poisonous = block.get("poisonous", False)
    frost = block.get("frost", False)

    return {
        'name': name,
        'weapon_type': weapon_type,
        'element': element,
        'minDamage': minDamage,
        'maxDamage': maxDamage,
        'upgrades': upgrades,
        'armorBonus': armorBonus,
        'speed': speed,
        'jump': jump,
        'attackCooldown': attackCooldown,
        'pierceCount': pierceCount,
        'enablePierceAreaDamage': enablePierceAreaDamage,
        'persistAgainstProjectile': persistAgainstProjectile,
        'poisonous': poisonous,
        'frost': frost
    }

def generate_weapon_code(data, weapon_type, secondary_types, list_name, drawable_prefix, default_name):
    code_list = []
    weapon_data = []

    if isinstance(data, list):
        for block in data:
            if isinstance(block, dict) and block.get("secondaryType") in secondary_types:
                fields = extract_common_fields(block, default_name, weapon_type)
                weapon_data.append(fields)

    weapon_data = sort_by_max_damage(weapon_data)

    for item in weapon_data:
        code = (
            f"{list_name}.add(new Weapon(str(context, R.string.{item['name']}), WeaponTypes.{item['weapon_type']}, "
            f"Elements.{item['element']}, {item['minDamage']}, {item['maxDamage']}, {item['upgrades']}, "
            f"{item['armorBonus']}, {item['speed']}, {item['jump']}, R.drawable.{drawable_prefix}_{item['name']}, "
            f"{item['attackCooldown']}, {item['pierceCount']}, {str(item['enablePierceAreaDamage']).lower()}, "
            f"{str(item['persistAgainstProjectile']).lower()}, {str(item['poisonous']).lower()}, {str(item['frost']).lower()}));"
        )
        code_list.append(code)

    return code_list

def generate_sword_code(data):
    return generate_weapon_code(data, "SWORD", ["sword"], "swordList", "sword", "test_sword")

def generate_hammer_code(data):
    return generate_weapon_code(data, "HAMMER", ["hammer", "mace"], "hammerList", "hammer", "test_hammer")

def generate_spear_code(data):
    return generate_weapon_code(data, "SPEAR", ["spear"], "spearList", "spear", "test_spear")

def generate_staff_code(data):
    return generate_weapon_code(data, "STAFF", ["staff", "grimoire"], "staffList", "staff", "test_staff")

def generate_dagger_code(data):
    return generate_weapon_code(data, "DAGGER", ["dagger"], "daggerList", "dagger", "test_dagger")

def generate_axe_code(data):
    return generate_weapon_code(data, "AXE", ["axe"], "axeList", "axe", "test_axe")
