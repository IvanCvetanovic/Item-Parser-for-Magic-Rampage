import tempfile
import unittest
from pathlib import Path

from class_parser import ClassParser

CLASS_CONTENT = """helmet1
{
    class = knight
    armorBoost = 1.2
}
hood1
{
    class = mage
    magicBoost = 1.5
}
"""


class ClassParserTests(unittest.TestCase):
    def _parser(self, tmp_dir):
        path = Path(tmp_dir) / "class-heads.enml"
        path.write_text(CLASS_CONTENT, encoding="utf-8")
        return ClassParser(str(path))

    def test_parse_file_reads_class_blocks(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            blocks = self._parser(tmp_dir).parse_file()
        data = [block.as_dict() for block in blocks]
        self.assertEqual([entry["class"] for entry in data], ["knight", "mage"])

    def test_generate_class_code(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            lines = self._parser(tmp_dir).generate_class_code()
        self.assertIn("ClassNames.KNIGHT", lines[0])
        self.assertIn("R.drawable.class_knight", lines[0])
        self.assertIn("ClassNames.MAGE", lines[1])

    def test_format_class_human(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            lines = self._parser(tmp_dir).format_class_human()
        self.assertIn("Class: Knight", lines[0])
        self.assertIn("Armor Bonus: 20%", lines[0])


if __name__ == "__main__":
    unittest.main()
