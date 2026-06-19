import tempfile
import unittest
from pathlib import Path

from enemy_parser import EnemyParser


class EnemyParserTests(unittest.TestCase):
    def test_parse_file_aggregates_sibling_equipped_items(self):
        # Real .character files hold a single character with equippedItem blocks
        # as siblings (not nested), so their stats are aggregated onto the enemy.
        content = """
character {
  resistance = 10;
  speed = 2;
}
equippedItem1 {
  damage = 3;
  speedBoost = 1.5;
}
equippedItem2 {
  damage = 7;
  speedBoost = 2;
}
"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "enemy.character"
            path.write_text(content, encoding="utf-8")
            parser = EnemyParser([tmp_dir])

            enemies = parser.parse_file(path)

        self.assertEqual(len(enemies), 1)
        self.assertEqual(enemies[0]["_items"]["damage"], 10)  # 3 + 7
        self.assertEqual(enemies[0]["_items"]["speedBoost"], 3.0)  # 1.5 * 2

    def test_parse_enemy_stats_supports_developer_mode(self):
        content = """
character {
  resistance = 10;
  speed = 2;
  jumpImpulse = 3;
  patrolBehaviour = "walk";
  attackBehaviour = "slash";
}
"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "slime.character"
            path.write_text(content, encoding="utf-8")
            parser = EnemyParser([tmp_dir])

            lines = parser.parse_enemy_stats(mode="developer")

        self.assertEqual(len(lines), 1)
        self.assertIn("enemyList.add(new Enemy(", lines[0])
        self.assertIn("R.drawable.enemy_slime", lines[0])


if __name__ == "__main__":
    unittest.main()
