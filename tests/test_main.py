import contextlib
import io
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

    def test_stdout_mode_prints_content_and_writes_no_files(self):
        with tempfile.TemporaryDirectory() as items_dir, \
                tempfile.TemporaryDirectory() as out_dir:
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed), contextlib.redirect_stderr(io.StringIO()):
                main([
                    "developer", "armor",
                    "--items-folder", items_dir,
                    "--output-dir", out_dir,
                    "--online-items-url", "",
                    "--stdout",
                    "--log-level", "critical",
                ])
            content = printed.getvalue()
            produced = list(Path(out_dir).iterdir())  # check before the temp dir is cleaned up
        self.assertEqual(produced, [])  # nothing written in --stdout mode
        self.assertIn("armor_code.txt", content)

    def test_summary_reports_missing_items_folder(self):
        with tempfile.TemporaryDirectory() as out_dir:
            report = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(report):
                main([
                    "normal", "armor",
                    "--items-folder", "Z:/definitely/missing",
                    "--output-dir", out_dir,
                    "--online-items-url", "",
                    "--log-level", "critical",
                ])
            text = report.getvalue()
        self.assertIn("(not found)", text)
        self.assertIn("Done:", text)


if __name__ == "__main__":
    unittest.main()
