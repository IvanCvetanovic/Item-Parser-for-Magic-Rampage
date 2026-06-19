import contextlib
import io
import os
import tempfile
import unittest

import language_getter as lg


class LanguageGetterHelpersTests(unittest.TestCase):
    def test_norm_key_collapses_separators(self):
        self.assertEqual(lg.norm_key("Skin-Black_Mage"), "skin_black_mage")
        self.assertEqual(lg.norm_key("  Foo--Bar  "), "foo_bar")
        self.assertEqual(lg.norm_key(""), "")

    def test_key_base_and_num_splits_trailing_digits(self):
        self.assertEqual(lg.key_base_and_num("skin_black_mage19"), ("skin_black_mage", "19"))
        self.assertEqual(lg.key_base_and_num("greeting"), ("greeting", None))

    def test_normalize_string_replaces_numbers_with_placeholder(self):
        self.assertEqual(lg.normalize_string("Deal 50 damage."), "deal <ph> damage")

    def test_normalize_string_drops_decoration_tags(self):
        self.assertEqual(lg.normalize_string("Hello <b>world</b>"), "hello world")

    def test_normalize_string_preserves_listed_tags(self):
        self.assertEqual(lg.normalize_string("Reached <new-game-plus>"), "reached <ph>")

    def test_parse_line(self):
        self.assertEqual(lg.parse_line("greeting = Hello;"), ("greeting", "Hello"))
        self.assertEqual(lg.parse_line("# comment"), (None, None))
        self.assertEqual(lg.parse_line("'quoted' = 'value';"), ("quoted", "value"))


class LanguageGetterDbTests(unittest.TestCase):
    def test_create_english_text_db_indexes_normalized_text(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with open(os.path.join(tmp_dir, "ui.strings"), "w", encoding="utf-8") as handle:
                handle.write("greeting = Hello 5 times\n")
            # Suppress progress prints (they contain emoji that crash on a
            # redirected non-UTF-8 stdout); we only care about the returned db.
            with contextlib.redirect_stdout(io.StringIO()):
                db = lg.create_english_text_db(tmp_dir)
        self.assertIn("hello <ph> times", db)
        self.assertEqual(db["hello <ph> times"], ("greeting", "ui.strings"))


if __name__ == "__main__":
    unittest.main()
