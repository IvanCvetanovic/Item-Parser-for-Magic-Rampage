import tempfile
import unittest
from pathlib import Path

from main import main


class MainAllModeTests(unittest.TestCase):
    def test_all_mode_exports_enemies(self):
        with tempfile.TemporaryDirectory() as items_dir, \
                tempfile.TemporaryDirectory() as enemy_dir, \
                tempfile.TemporaryDirectory() as out_dir:
            (Path(enemy_dir) / "slime.character").write_text(
                "character {\n  resistance = 10;\n  speed = 1;\n}\n",
                encoding="utf-8",
            )
            # Empty URL fails fast (no network) -> offline fallback / empty items;
            # enemy export is independent and must still run in "all" mode.
            main([
                "developer", "all",
                "--items-folder", items_dir,
                "--enemy-dir", enemy_dir,
                "--output-dir", out_dir,
                "--online-items-url", "",
                "--log-level", "critical",
            ])
            produced = {path.name for path in Path(out_dir).iterdir()}
        self.assertIn("enemy_code.txt", produced)


if __name__ == "__main__":
    unittest.main()
