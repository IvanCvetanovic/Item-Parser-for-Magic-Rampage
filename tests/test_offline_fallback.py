import json
import tempfile
import unittest
from pathlib import Path

from online_data import OnlineDataManager


class OfflineFallbackTests(unittest.TestCase):
    def test_falls_back_to_bundled_data_when_fetch_fails(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            bundled = Path(tmp_dir) / "items.json"
            bundled.write_text(
                json.dumps([
                    {"name": "Holy Sword", "type": "weapon", "secondaryType": "sword"},
                ]),
                encoding="utf-8",
            )
            manager = OnlineDataManager(bundled_items_path=bundled)
            # An empty URL makes the fetch fail immediately (no network), so the
            # bundled snapshot should be used instead.
            data = manager.get_online_item_data("")
        self.assertEqual([item["name"] for item in data], ["Holy Sword"])

    def test_returns_none_when_no_bundled_file(self):
        manager = OnlineDataManager(bundled_items_path=Path("does-not-exist.json"))
        self.assertIsNone(manager.get_online_item_data(""))


if __name__ == "__main__":
    unittest.main()
