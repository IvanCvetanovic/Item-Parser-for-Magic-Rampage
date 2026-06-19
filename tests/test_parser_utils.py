import unittest

from parser_utils import parse_scalar, process_boost, sanitize_resource_name


class ParseScalarTests(unittest.TestCase):
    def test_booleans(self):
        self.assertIs(parse_scalar("true"), True)
        self.assertIs(parse_scalar("False"), False)

    def test_integers_and_floats(self):
        self.assertEqual(parse_scalar("42"), 42)
        self.assertEqual(parse_scalar("-7"), -7)
        self.assertEqual(parse_scalar("3.14"), 3.14)
        self.assertEqual(parse_scalar(".5"), 0.5)

    def test_trailing_semicolon_and_whitespace(self):
        self.assertEqual(parse_scalar("10;"), 10)
        self.assertEqual(parse_scalar("1.5;"), 1.5)
        self.assertEqual(parse_scalar("  42  "), 42)

    def test_plain_string_passthrough(self):
        self.assertEqual(parse_scalar("Holy Sword"), "Holy Sword")

    def test_non_string_returned_unchanged(self):
        self.assertEqual(parse_scalar(5), 5)
        self.assertIsNone(parse_scalar(None))


class ProcessBoostTests(unittest.TestCase):
    def test_neutral_multipliers_are_zero(self):
        self.assertEqual(process_boost(1), 0)
        self.assertEqual(process_boost(0), 0)

    def test_positive_and_negative_bonus(self):
        self.assertEqual(process_boost(1.5), 50)
        self.assertEqual(process_boost(2), 100)
        self.assertEqual(process_boost(0.9), -10)

    def test_invalid_values_default_to_zero(self):
        self.assertEqual(process_boost("abc"), 0)
        self.assertEqual(process_boost(None), 0)


class SanitizeResourceNameTests(unittest.TestCase):
    def test_spaces_and_apostrophes(self):
        self.assertEqual(sanitize_resource_name("Knight's Armor", "x"), "knights_armor")

    def test_hyphen_removed_and_plus_expanded(self):
        self.assertEqual(sanitize_resource_name("Fire-Axe", "x"), "fireaxe")
        self.assertEqual(sanitize_resource_name("Sword +1", "x"), "sword__plus1")

    def test_fallback_used_for_empty(self):
        self.assertEqual(sanitize_resource_name("", "test_sword"), "test_sword")
        self.assertEqual(sanitize_resource_name(None, "test_ring"), "test_ring")


if __name__ == "__main__":
    unittest.main()
