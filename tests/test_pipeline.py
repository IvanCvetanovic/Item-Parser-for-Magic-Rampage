import unittest

from pipeline import ItemPipeline


class ItemPipelineTests(unittest.TestCase):
    def test_reclassify_axes_and_hammers_moves_maces_to_hammer(self):
        data = {
            "axe": [
                {"name": "Axe", "secondaryType": "axe"},
                {"name": "Mace", "secondaryType": "mace"},
            ],
            "hammer": [{"name": "Hammer", "secondaryType": "hammer"}],
        }

        result = ItemPipeline.reclassify_axes_and_hammers(data)

        self.assertEqual([item["name"] for item in result["axe"]], ["Axe"])
        self.assertEqual([item["name"] for item in result["hammer"]], ["Hammer", "Mace"])

    def test_sort_grouped_items_uses_stable_item_specific_sorting(self):
        data = {
            "sword": [
                {"name": "B", "damage": 10, "maxLevelDamage": 50},
                {"name": "A", "damage": 10, "maxLevelDamage": 20},
            ],
            "armor": [
                {"name": "Heavy", "armor": 10, "maxLevelArmor": 100},
                {"name": "Light", "armor": 5, "maxLevelArmor": 40},
            ],
        }

        result = ItemPipeline.sort_grouped_items(data)

        self.assertEqual([item.as_dict()["name"] for item in result["sword"]], ["A", "B"])
        self.assertEqual([item.as_dict()["name"] for item in result["armor"]], ["Light", "Heavy"])


if __name__ == "__main__":
    unittest.main()
