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

# For speed and jump
def process_boost(value):
    return 0 if value == 1 else int((value - 1) * 100)

# for other weapon boni
def process_boost_extra(value):
    return 0 if value == 1 else int((value * 100) - 100)

def clean_name(name):
    if name:
        name = name.replace("'", "")
        name = name.replace("+", "_plus")
    return name

def sort_by_max_damage(weapon_list):
    return sorted(weapon_list, key=lambda x: x['maxDamage'])

def generate_sword_code(data):
    sword_code_list = []

    if isinstance(data, list):
        sword_data = []
        for block in data:
            if isinstance(block, dict) and block.get("secondaryType") == "sword":
                name = block.get("name", "test_sword").replace(" ", "_").lower()
                weapon_type = "SWORD"
                element = block.get("element", "NEUTRAL").upper()
                if not element:
                    element = "NEUTRAL"

                minDamage = block.get("damage", 0)
                maxDamage = block.get("maxLevelDamage", 0)
                upgrades = block.get("maxLevelAllowed", 0)
                armorBonus = process_boost_extra(block.get("armorBoost", 1))
                speed = process_boost(block.get("speedBoost", 1))
                jump = process_boost(block.get("jumpBoost", 1))

                sword_data.append({
                    'name': name,
                    'weapon_type': weapon_type,
                    'element': element,
                    'minDamage': minDamage,
                    'maxDamage': maxDamage,
                    'upgrades': upgrades,
                    'armorBonus': armorBonus,
                    'speed': speed,
                    'jump': jump
                })

        sword_data = sort_by_max_damage(sword_data)

        for item in sword_data:
            code = (
                f"swordList.add(createWeapon(R.string.{item['name']}, WeaponTypes.{item['weapon_type']}, "
                f"Elements.{item['element']}, {item['minDamage']}, {item['maxDamage']}, {item['upgrades']}, "
                f"{item['armorBonus']}, {item['speed']}, {item['jump']}, "
                f"R.drawable.sword_{item['name']}));"
            )
            sword_code_list.append(code)

    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                sword_code_list.extend(generate_sword_code(value))  # Recursive call

    return sword_code_list


def generate_hammer_code(data):
    hammer_code_list = []

    if isinstance(data, list):
        for block in data:
            if isinstance(block, dict) and block.get("secondaryType") == "hammer":
                name = block.get("name", "test_hammer").replace(" ", "_").lower()
                weapon_type = "HAMMER"
                element = block.get("element", "NEUTRAL").upper()
                if not element:
                    element = "NEUTRAL"
                minDamage = block.get("damage", 0)
                maxDamage = block.get("maxLevelDamage", 0)
                upgrades = block.get("maxLevelAllowed", 0)
                armorBonus = process_boost_extra(block.get("armorBoost", 1))
                speed = process_boost(block.get("speedBoost", 1))
                jump = process_boost(block.get("jumpBoost", 1))

                hammer_code_list.append({
                    'name': name,
                    'weapon_type': weapon_type,
                    'element': element,
                    'minDamage': minDamage,
                    'maxDamage': maxDamage,
                    'upgrades': upgrades,
                    'armorBonus': armorBonus,
                    'speed': speed,
                    'jump': jump
                })

    hammer_code_list = sort_by_max_damage(hammer_code_list)
    code_list = [
        f"hammerList.add(createWeapon(R.string.{item['name']}, WeaponTypes.{item['weapon_type']}, "
        f"Elements.{item['element']}, {item['minDamage']}, {item['maxDamage']}, {item['upgrades']}, "
        f"{item['armorBonus']}, {item['speed']}, {item['jump']}, R.drawable.hammer_{item['name']}));"
        for item in hammer_code_list
    ]

    return code_list


def generate_spear_code(data):
    spear_code_list = []

    if isinstance(data, list):
        for block in data:
            if isinstance(block, dict) and block.get("secondaryType") == "spear":
                name = block.get("name", "test_spear").replace(" ", "_").lower()
                weapon_type = "SPEAR"
                element = block.get("element", "NEUTRAL").upper()
                if not element:
                    element = "NEUTRAL"
                minDamage = block.get("damage", 0)
                maxDamage = block.get("maxLevelDamage", 0)
                upgrades = block.get("maxLevelAllowed", 0)
                armorBonus = process_boost_extra(block.get("armorBoost", 1))
                speed = process_boost(block.get("speedBoost", 1))
                jump = process_boost(block.get("jumpBoost", 1))

                spear_code_list.append({
                    'name': name,
                    'weapon_type': weapon_type,
                    'element': element,
                    'minDamage': minDamage,
                    'maxDamage': maxDamage,
                    'upgrades': upgrades,
                    'armorBonus': armorBonus,
                    'speed': speed,
                    'jump': jump
                })

    spear_code_list = sort_by_max_damage(spear_code_list)
    code_list = [
        f"spearList.add(createWeapon(R.string.{item['name']}, WeaponTypes.{item['weapon_type']}, "
        f"Elements.{item['element']}, {item['minDamage']}, {item['maxDamage']}, {item['upgrades']}, "
        f"{item['armorBonus']}, {item['speed']}, {item['jump']}, R.drawable.spear_{item['name']}));"
        for item in spear_code_list
    ]

    return code_list


def generate_staff_code(data):
    staff_code_list = []

    if isinstance(data, list):
        for block in data:
            if isinstance(block, dict) and block.get("secondaryType") == "staff":
                name = block.get("name", "test_staff").replace(" ", "_").lower()
                weapon_type = "STAFF"
                element = block.get("element", "NEUTRAL").upper()
                if not element:
                    element = "NEUTRAL"
                minDamage = block.get("damage", 0)
                maxDamage = block.get("maxLevelDamage", 0)
                upgrades = block.get("maxLevelAllowed", 0)
                armorBonus = process_boost_extra(block.get("armorBoost", 1))
                speed = process_boost(block.get("speedBoost", 1))
                jump = process_boost(block.get("jumpBoost", 1))

                staff_code_list.append({
                    'name': name,
                    'weapon_type': weapon_type,
                    'element': element,
                    'minDamage': minDamage,
                    'maxDamage': maxDamage,
                    'upgrades': upgrades,
                    'armorBonus': armorBonus,
                    'speed': speed,
                    'jump': jump
                })

    staff_code_list = sort_by_max_damage(staff_code_list)
    code_list = [
        f"staffList.add(createWeapon(R.string.{item['name']}, WeaponTypes.{item['weapon_type']}, "
        f"Elements.{item['element']}, {item['minDamage']}, {item['maxDamage']}, {item['upgrades']}, "
        f"{item['armorBonus']}, {item['speed']}, {item['jump']}, R.drawable.staff_{item['name']}));"
        for item in staff_code_list
    ]

    return code_list


def generate_dagger_code(data):
    dagger_code_list = []

    if isinstance(data, list):
        for block in data:
            if isinstance(block, dict) and block.get("secondaryType") == "dagger":
                name = block.get("name", "test_dagger").replace(" ", "_").lower()
                weapon_type = "DAGGER"
                element = block.get("element", "NEUTRAL").upper()
                if not element:
                    element = "NEUTRAL"
                minDamage = block.get("damage", 0)
                maxDamage = block.get("maxLevelDamage", 0)
                upgrades = block.get("maxLevelAllowed", 0)
                armorBonus = process_boost_extra(block.get("armorBoost", 1))
                speed = process_boost(block.get("speedBoost", 1))
                jump = process_boost(block.get("jumpBoost", 1))

                dagger_code_list.append({
                    'name': name,
                    'weapon_type': weapon_type,
                    'element': element,
                    'minDamage': minDamage,
                    'maxDamage': maxDamage,
                    'upgrades': upgrades,
                    'armorBonus': armorBonus,
                    'speed': speed,
                    'jump': jump
                })

    dagger_code_list = sort_by_max_damage(dagger_code_list)
    code_list = [
        f"daggerList.add(createWeapon(R.string.{item['name']}, WeaponTypes.{item['weapon_type']}, "
        f"Elements.{item['element']}, {item['minDamage']}, {item['maxDamage']}, {item['upgrades']}, "
        f"{item['armorBonus']}, {item['speed']}, {item['jump']}, R.drawable.dagger_{item['name']}));"
        for item in dagger_code_list
    ]

    return code_list


def generate_axe_code(data):
    axe_code_list = []

    if isinstance(data, list):
        for block in data:
            if isinstance(block, dict) and block.get("secondaryType") == "axe":
                name = block.get("name", "test_axe").replace(" ", "_").lower()
                weapon_type = "AXE"
                element = block.get("element", "NEUTRAL").upper()
                if not element:
                    element = "NEUTRAL"
                minDamage = block.get("damage", 0)
                maxDamage = block.get("maxLevelDamage", 0)
                upgrades = block.get("maxLevelAllowed", 0)
                armorBonus = process_boost_extra(block.get("armorBoost", 1))
                speed = process_boost(block.get("speedBoost", 1))
                jump = process_boost(block.get("jumpBoost", 1))

                axe_code_list.append({
                    'name': name,
                    'weapon_type': weapon_type,
                    'element': element,
                    'minDamage': minDamage,
                    'maxDamage': maxDamage,
                    'upgrades': upgrades,
                    'armorBonus': armorBonus,
                    'speed': speed,
                    'jump': jump
                })

    axe_code_list = sort_by_max_damage(axe_code_list)
    code_list = [
        f"axeList.add(createWeapon(R.string.{item['name']}, WeaponTypes.{item['weapon_type']}, "
        f"Elements.{item['element']}, {item['minDamage']}, {item['maxDamage']}, {item['upgrades']}, "
        f"{item['armorBonus']}, {item['speed']}, {item['jump']}, R.drawable.axe_{item['name']}));"
        for item in axe_code_list
    ]

    return code_list

