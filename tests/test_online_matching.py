import unittest

from online_data import OnlineDataManager, _matches, _norm_key, _strip_type_suffix


class OnlineMatchingHelpersTests(unittest.TestCase):
    def test_norm_key_strips_accents_and_punctuation(self):
        self.assertEqual(_norm_key("Café Sword!"), "cafe sword")
        self.assertEqual(_norm_key("  Holy   Blade  "), "holy blade")

    def test_strip_type_suffix(self):
        self.assertEqual(_strip_type_suffix("Holy Sword", "sword"), "holy")
        self.assertEqual(_strip_type_suffix("Holy Sword", "axe"), "holy sword")

    def test_matches_by_english_name(self):
        self.assertTrue(_matches("holy sword", {"name_en": "Holy Sword"}, "sword"))
        self.assertFalse(_matches("holy sword", {"name": "Dark Axe"}, "sword"))

    def test_matches_by_sprite_fallback(self):
        self.assertTrue(_matches("ring of power", {"sprite": "Ring Of Power"}, "ring"))


class MergeOnlineFieldsTests(unittest.TestCase):
    def test_merge_copies_max_damage_and_prices(self):
        local = {"sword": [{"name": "Holy Sword", "damage": 10}]}
        online = [{
            "name_en": "Holy Sword",
            "type": "weapon",
            "secondaryType": "sword",
            "maxLevelDamage": 99,
            "freemiumGoldPrice": 500,
        }]
        merged = OnlineDataManager().merge_online_fields(local, online)
        self.assertEqual(merged["sword"][0]["maxLevelDamage"], 99)
        self.assertEqual(merged["sword"][0]["freemiumGoldPrice"], 500)


if __name__ == "__main__":
    unittest.main()
