import unittest

from weapon_parser import extract_common_fields, generate_sword_code


class WeaponParserTests(unittest.TestCase):
    def test_extract_common_fields_normalizes_name_and_damage(self):
        fields = extract_common_fields(
            {"name": "Fire Sword", "damage": 10, "maxLevelDamage": 50, "element": "fire"},
            "test_sword",
            "SWORD",
        )
        self.assertEqual(fields["name"], "fire_sword")
        self.assertEqual(fields["minDamage"], 10)
        self.assertEqual(fields["maxDamage"], 50)
        self.assertEqual(fields["element"], "FIRE")
        self.assertEqual(fields["weapon_type"], "SWORD")

    def test_generate_sword_code_emits_constructor_line(self):
        lines = generate_sword_code([
            {"name": "Fire Sword", "damage": 10, "maxLevelDamage": 50, "element": "fire"},
        ])
        self.assertEqual(len(lines), 1)
        self.assertIn("swordList.add(new Weapon(", lines[0])
        self.assertIn("R.string.fire_sword", lines[0])
        self.assertIn("WeaponTypes.SWORD", lines[0])
        self.assertIn("Elements.FIRE", lines[0])
        self.assertTrue(lines[0].endswith("));"))


if __name__ == "__main__":
    unittest.main()
