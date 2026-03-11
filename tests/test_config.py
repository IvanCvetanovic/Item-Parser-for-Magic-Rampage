import os
import unittest
from config import parse_args


class ConfigTests(unittest.TestCase):
    def test_parse_args_supports_overrides(self):
        config = parse_args([
            "developer",
            "enemy",
            "--items-folder",
            "items-dir",
            "--enemy-dir",
            "enemy-a",
            "--enemy-dir",
            "enemy-b",
            "--output-dir",
            "out",
            "--log-level",
            "debug",
        ])

        self.assertEqual(config.output_type, "developer")
        self.assertEqual(config.item_type, "enemy")
        self.assertEqual(str(config.items_folder), "items-dir")
        self.assertEqual([str(path) for path in config.enemy_directories], ["enemy-a", "enemy-b"])
        self.assertEqual(str(config.output_dir), "out")
        self.assertEqual(config.log_level, "DEBUG")

    def test_parse_args_uses_enemy_env_var(self):
        original = os.environ.get("MAGIC_RAMPAGE_ENEMY_DIRS")
        os.environ["MAGIC_RAMPAGE_ENEMY_DIRS"] = os.pathsep.join(["env-a", "env-b"])
        try:
            config = parse_args([])
        finally:
            if original is None:
                os.environ.pop("MAGIC_RAMPAGE_ENEMY_DIRS", None)
            else:
                os.environ["MAGIC_RAMPAGE_ENEMY_DIRS"] = original

        self.assertEqual([str(path) for path in config.enemy_directories], ["env-a", "env-b"])


if __name__ == "__main__":
    unittest.main()
