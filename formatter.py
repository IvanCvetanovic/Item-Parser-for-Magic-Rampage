# formatter.py
class OutputFormatter:
    @staticmethod
    def process_boost(value):
        return 0 if value == 0 or value == 1 else round((value - 1) * 100)

    @classmethod
    def format_human_armor(cls, items):
        lines = []
        for item in items:
            name = item.get("name", "Unknown").replace("_", " ").title()
            element = item.get("element", "NEUTRAL").title()
            frost = item.get("frost", False)
            frost_str = "Yes" if frost else "No"
            min_armor = item.get("armor", 0)
            max_armor = item.get("maxLevelArmor", min_armor)
            upgrades = item.get("maxLevelAllowed", 1)
            speed = cls.process_boost(item.get("speedBoost", 1))
            jump = cls.process_boost(item.get("jumpBoost", 1))
            magic = cls.process_boost(item.get("magicBoost", 1))
            line = (f"Armor: {name}, Element: {element}, Immune to Frost: {frost_str}, "
                    f"Min Armor: {min_armor}, Max Armor: {max_armor}, Upgrades: {upgrades}, "
                    f"Speed: {speed}%, Jump: {jump}%, Magic: {magic}%")
            lines.append(line)
        return "\n".join(lines)

    @classmethod
    def format_human_weapon(cls, items):
        lines = []
        for item in items:
            name = item.get("name", "Unknown").replace("_", " ").title()
            weapon_type = item.get("weapon_type", "Unknown").title()
            element = item.get("element", "NEUTRAL").title()
            min_damage = item.get("damage", 0)
            max_damage = item.get("maxLevelDamage", item.get("damage", 0))
            upgrades = item.get("maxLevelAllowed", 1)
            armor_bonus = cls.process_boost(item.get("armorBoost", 1))
            speed = cls.process_boost(item.get("speedBoost", 1))
            jump = cls.process_boost(item.get("jumpBoost", 1))
            attack_cd = item.get("attackCooldown", 0)
            pierce_count = item.get("pierceCount", 0)
            enable_pierce_str = "Yes" if item.get("enablePierceAreaDamage", False) else "No"
            persist_str = "Yes" if item.get("persistAgainstProjectile", False) else "No"
            poisonous_str = "Yes" if item.get("poisonous", False) else "No"
            frost_str = "Yes" if item.get("frost", False) else "No"
            line = (f"Weapon: {name}, Type: {weapon_type}, Element: {element}, Min Damage: {min_damage}, "
                    f"Max Damage: {max_damage}, Upgrades: {upgrades}, Armor Bonus: {armor_bonus}%, Speed: {speed}%, "
                    f"Jump: {jump}%, Attack Cooldown: {attack_cd}, Pierce Count: {pierce_count}, "
                    f"Pierce: {enable_pierce_str}, Persist: {persist_str}, Poisonous: {poisonous_str}, Frost: {frost_str}")
            lines.append(line)
        return "\n".join(lines)

    @classmethod
    def format_human_ring(cls, items):
        lines = []
        for item in items:
            name = item.get("name", "Unknown").replace("_", " ").title()
            element = item.get("element", "NEUTRAL").title()
            armor = item.get("armor", 0)
            armor_bonus = cls.process_boost(item.get("armorBoost", 1))
            speed = cls.process_boost(item.get("speedBoost", 1))
            jump = cls.process_boost(item.get("jumpBoost", 1))
            magic = cls.process_boost(item.get("magicBoost", 1))
            line = (f"Ring: {name}, Element: {element}, Armor: {armor}, Armor Bonus: {armor_bonus}%, "
                    f"Speed: {speed}%, Jump: {jump}%, Magic: {magic}%")
            lines.append(line)
        return "\n".join(lines)
