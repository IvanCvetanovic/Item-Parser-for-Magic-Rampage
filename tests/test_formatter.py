import unittest

from formatter import OutputFormatter


class OutputFormatterTests(unittest.TestCase):
    def test_process_boost(self):
        self.assertEqual(OutputFormatter.process_boost(1), 0)
        self.assertEqual(OutputFormatter.process_boost(0), 0)
        self.assertEqual(OutputFormatter.process_boost(1.25), 25)

    def test_price_suffix_omits_missing_values(self):
        suffix = OutputFormatter._price_suffix({"freemiumGoldPrice": 100})
        self.assertEqual(suffix, " Freemium Gold Price: 100")
        self.assertEqual(OutputFormatter._price_suffix({}), "")

    def test_format_human_armor(self):
        items = [{"name": "holy_armor", "element": "fire", "armor": 10, "maxLevelArmor": 50}]
        out = OutputFormatter.format_human_armor(items)
        self.assertIn("Armor: Holy Armor", out)
        self.assertIn("Element: Fire", out)
        self.assertIn("Max Armor: 50", out)
        self.assertIn("Immune to Frost: No", out)

    def test_format_human_weapon_uses_default_type(self):
        items = [{"name": "fire_sword", "damage": 10, "maxLevelDamage": 50}]
        out = OutputFormatter.format_human_weapon(items, default_weapon_type="sword")
        self.assertIn("Weapon: Fire Sword", out)
        self.assertIn("Type: Sword", out)
        self.assertIn("Max Damage: 50", out)

    def test_format_human_ring(self):
        items = [{"name": "power_ring", "element": "neutral", "armor": 3}]
        out = OutputFormatter.format_human_ring(items)
        self.assertIn("Ring: Power Ring", out)
        self.assertIn("Armor: 3", out)


if __name__ == "__main__":
    unittest.main()
