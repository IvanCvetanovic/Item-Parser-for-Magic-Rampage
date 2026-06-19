import tempfile
import unittest
from pathlib import Path

from file_parser import FileParser


class FileParserTests(unittest.TestCase):
    def test_parse_enml_block_strips_inline_comments(self):
        parser = FileParser("ignored", {})
        block = "name = Holy Sword\ndamage = 10 // inline comment\nfrost = true"
        result = parser.parse_enml_block(block)
        self.assertEqual(result["name"], "Holy Sword")
        self.assertEqual(result["damage"], 10)
        self.assertIs(result["frost"], True)

    def test_parse_files_uses_file_to_type_mapping(self):
        content = "item\n{\n    name = Holy Sword\n    damage = 10\n}\n"
        with tempfile.TemporaryDirectory() as tmp_dir:
            (Path(tmp_dir) / "weapon-sword-1.enml").write_text(content, encoding="utf-8")
            (Path(tmp_dir) / "ignored.txt").write_text("noise", encoding="utf-8")
            parser = FileParser(tmp_dir, {"weapon-sword-1.enml": "sword"})
            result = parser.parse_files()
        self.assertEqual(len(result["sword"]), 1)
        self.assertEqual(result["sword"][0]["name"], "Holy Sword")
        self.assertEqual(result["sword"][0]["damage"], 10)

    def test_parse_files_missing_folder_returns_empty_groups(self):
        parser = FileParser("does-not-exist", {"weapon-sword-1.enml": "sword"})
        result = parser.parse_files()
        self.assertEqual(result, {"sword": []})


if __name__ == "__main__":
    unittest.main()
