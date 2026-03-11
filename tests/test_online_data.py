import unittest
from online_data import OnlineDataManager


class OnlineDataTests(unittest.TestCase):
    def test_convert_online_to_local_groups_supported_item_types(self):
        items = [
            {"type": "weapon", "secondaryType": "sword", "name": "Sword"},
            {"type": "armor", "secondaryType": "armor", "name": "Armor"},
            {"type": "supply", "secondaryType": "ring", "name": "Ring"},
            {"type": "supply", "secondaryType": "essence", "name": "Ignored"},
        ]

        converted = OnlineDataManager().convert_online_to_local(items)

        self.assertEqual([item["name"] for item in converted["sword"]], ["Sword"])
        self.assertEqual([item["name"] for item in converted["armor"]], ["Armor"])
        self.assertEqual([item["name"] for item in converted["ring"]], ["Ring"])
        self.assertEqual(converted["axe"], [])

    def test_validate_online_item_data_skips_missing_required_fields(self):
        data = [
            {"name": "Valid", "type": "weapon", "secondaryType": "sword"},
            {"name": "Missing type"},
        ]

        validated = OnlineDataManager().validate_online_item_data(data)

        self.assertEqual(len(validated), 1)
        self.assertEqual(validated[0]["name"], "Valid")


if __name__ == "__main__":
    unittest.main()
