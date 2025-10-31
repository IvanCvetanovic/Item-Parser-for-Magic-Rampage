def process_boost(value):
    return 0 if value == 0 or value == 1 else round((value - 1) * 100)


def sort_by_max_armor(items, is_ring=False):
    """Sorts a list of dicts by max armor (or armor if ring) in ascending order."""
    if is_ring:
        return sorted(items, key=lambda x: x.get("armor", 0))
    else:
        return sorted(items, key=lambda x: x.get("maxLevelArmor", x.get("armor", 0)))


def _price_values_in_order(block):
    """Return exactly six price values in required order, defaulting to 0 if missing."""
    order = [
        "freemiumGoldPrice",
        "premiumGoldPrice",
        "freemiumCoinPrice",
        "premiumCoinPrice",
        "baseFreemiumSellPrice",
        "basePremiumSellPrice",
    ]
    vals = []
    for key in order:
        v = block.get(key)
        vals.append(0 if v is None else v)
    return vals


def _append_price_params(code_so_far, block):
    """Append the six numeric price params to the constructor call, then close '));'."""
    vals = _price_values_in_order(block)
    return code_so_far + ", " + ", ".join(str(v) for v in vals) + "));"


def generate_armor_code(data):
    armor_code_list = []

    if isinstance(data, list):
        # sort ascending
        sorted_data = sort_by_max_armor(data, is_ring=False)

        for block in sorted_data:
            if isinstance(block, dict):
                name = (block.get("name", "test_armor")
                        .replace(" ", "_").replace("'", "")
                        .replace("+", "_plus").replace("-", "")
                        .lower())
                frostImmune = block.get("frost", False)
                minArmor = block.get("armor", 0)
                maxArmor = block.get("maxLevelArmor", minArmor)
                upgrades = block.get("maxLevelAllowed", 1) or 1

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

                base = (
                    f"armorList.add(new Armor(str(context, R.string.{name}), Elements.{element}, "
                    f"{str(frostImmune).lower()}, {minArmor}, {maxArmor}, {upgrades}, "
                    f"{speed}, {jump}, {magic}, {sword}, "
                    f"{staff}, {dagger}, {axe}, {hammer}, {spear}, "
                    f"R.drawable.armor_{name}"
                )
                code = _append_price_params(base, block)
                armor_code_list.append(code)

    return armor_code_list


def generate_ring_code(data):
    ring_code_list = []

    if isinstance(data, list):
        # sort ascending
        sorted_data = sort_by_max_armor(data, is_ring=True)

        for block in sorted_data:
            if isinstance(block, dict):
                name = (block.get("name", "test_ring")
                        .replace(" ", "_").replace("'", "")
                        .replace("+", "_plus").replace("-", "")
                        .lower())
                element = block.get("element", "NEUTRAL").upper()
                armor = block.get("armor", 0)
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

                base = (
                    f"ringList.add(new Ring(str(context, R.string.{name}), Elements.{element}, "
                    f"{armor}, {armorBonus}, {speed}, {jump}, {magic}, {sword}, "
                    f"{staff}, {dagger}, {axe}, {hammer}, {spear}, "
                    f"R.drawable.ring_{name}"
                )
                code = _append_price_params(base, block)
                ring_code_list.append(code)

    return ring_code_list
