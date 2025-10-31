def process_boost(value):
    """Converts boost multipliers to percentages (e.g. 1.2 → 20)."""
    return 0 if value in (0, 1) else round((value - 1) * 100)


def sort_by_max_damage(weapon_list):
    """Sort weapons by their max damage."""
    return sorted(weapon_list, key=lambda x: x['maxDamage'])


def extract_common_fields(block, default_name, weapon_type):
    """Extract shared weapon properties and compute damage/boost values."""
    name = block.get("name", default_name) \
                .replace(" ", "_") \
                .replace("'", "") \
                .replace("+", "_plus") \
                .replace("-", "") \
                .lower()

    element = block.get("element", "NEUTRAL").upper() or "NEUTRAL"

    # Damage handling — if no maxLevelDamage, fallback to local 'damage'
    min_dmg = block.get("damage", 0)
    max_dmg = (
        block.get("maxLevelDamage")
        or block.get("maxleveldamage")
        or block.get("max_damage")
        or block.get("damage", 0)
    )

    upgrades = block.get("maxLevelAllowed", 0) or 1
    armor_bonus = process_boost(block.get("armorBoost", 1))
    speed = process_boost(block.get("speedBoost", 1))
    jump = process_boost(block.get("jumpBoost", 1))
    attack_cd = block.get("attackCooldown", 0)
    pierce = block.get("pierceCount", 0)
    pierce_area = block.get("enablePierceAreaDamage", False)
    persist = block.get("persistAgainstProjectile", False)
    poisonous = block.get("poisonous", False)
    frost = block.get("frost", False)

    # Prices
    fg = block.get("freemiumGoldPrice", 0)
    pg = block.get("premiumGoldPrice", 0)
    fc = block.get("freemiumCoinPrice", 0)
    pc = block.get("premiumCoinPrice", 0)
    sf = block.get("baseFreemiumSellPrice", 0)
    sp = block.get("basePremiumSellPrice", 0)

    return {
        "name": name,
        "weapon_type": weapon_type,
        "element": element,
        "minDamage": min_dmg,
        "maxDamage": max_dmg,
        "upgrades": upgrades,
        "armorBonus": armor_bonus,
        "speed": speed,
        "jump": jump,
        "attackCooldown": attack_cd,
        "pierceCount": pierce,
        "enablePierceAreaDamage": pierce_area,
        "persistAgainstProjectile": persist,
        "poisonous": poisonous,
        "frost": frost,
        "freemiumGoldPrice": fg,
        "premiumGoldPrice": pg,
        "freemiumCoinPrice": fc,
        "premiumCoinPrice": pc,
        "baseFreemiumSellPrice": sf,
        "basePremiumSellPrice": sp
    }


def generate_weapon_code(data, weapon_type, list_name, drawable_prefix, default_name):
    """Generate full developer-style code lines for each weapon."""
    code_list = []
    weapon_data = []

    if isinstance(data, list):
        for block in data:
            if isinstance(block, dict):
                fields = extract_common_fields(block, default_name, weapon_type)
                weapon_data.append(fields)

    weapon_data = sort_by_max_damage(weapon_data)

    for item in weapon_data:
        code = (
            f"{list_name}.add(new Weapon("
            f"str(context, R.string.{item['name']}), "
            f"WeaponTypes.{item['weapon_type']}, "
            f"Elements.{item['element']}, "
            f"{item['minDamage']}, {item['maxDamage']}, "
            f"{item['upgrades']}, {item['armorBonus']}, "
            f"{item['speed']}, {item['jump']}, "
            f"R.drawable.{drawable_prefix}_{item['name']}, "
            f"{item['attackCooldown']}, {item['pierceCount']}, "
            f"{str(item['enablePierceAreaDamage']).lower()}, "
            f"{str(item['persistAgainstProjectile']).lower()}, "
            f"{str(item['poisonous']).lower()}, {str(item['frost']).lower()}, "
            f"{item['freemiumGoldPrice']}, {item['premiumGoldPrice']}, "
            f"{item['freemiumCoinPrice']}, {item['premiumCoinPrice']}, "
            f"{item['baseFreemiumSellPrice']}, {item['basePremiumSellPrice']}));"
        )
        code_list.append(code)

    return code_list


# Shortcuts for specific weapon categories
def generate_sword_code(data):
    return generate_weapon_code(data, "SWORD", "swordList", "sword", "test_sword")


def generate_hammer_code(data):
    return generate_weapon_code(data, "HAMMER", "hammerList", "hammer", "test_hammer")


def generate_spear_code(data):
    return generate_weapon_code(data, "SPEAR", "spearList", "spear", "test_spear")


def generate_staff_code(data):
    return generate_weapon_code(data, "STAFF", "staffList", "staff", "test_staff")


def generate_dagger_code(data):
    return generate_weapon_code(data, "DAGGER", "daggerList", "dagger", "test_dagger")


def generate_axe_code(data):
    return generate_weapon_code(data, "AXE", "axeList", "axe", "test_axe")
