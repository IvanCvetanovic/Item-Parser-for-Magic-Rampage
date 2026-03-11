import argparse
import logging
import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ITEMS_FOLDER = r"C:\Program Files (x86)\Steam\steamapps\common\Magic Rampage\items"
DEFAULT_ENEMY_DIRECTORIES = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Magic Rampage\npcs\enemies",
    r"C:\Program Files (x86)\Steam\steamapps\common\Magic Rampage\npcs\bosses",
]
DEFAULT_ONLINE_ITEMS_URL = "https://gist.githubusercontent.com/andresan87/5670c559e5a930129aa03dfce7827306/raw/items.json"
DEFAULT_OUTPUT_DIR = "output"
OUTPUT_TYPES = ("developer", "normal")
ITEM_TYPES = ("armor", "ring", "sword", "hammer", "spear", "staff", "dagger", "axe", "all", "class", "enemy")


@dataclass(frozen=True)
class AppConfig:
    output_type: str
    item_type: str
    items_folder: Path
    enemy_directories: tuple[Path, ...]
    online_items_url: str
    output_dir: Path
    log_level: str


def _split_env_paths(value):
    if not value:
        return None
    parts = [part.strip() for part in value.split(os.pathsep) if part.strip()]
    return tuple(Path(part) for part in parts) if parts else None


def parse_args(argv=None):
    parser = argparse.ArgumentParser("Parse Magic Rampage ENML files")
    parser.add_argument("output_type", choices=OUTPUT_TYPES, nargs="?", default="normal")
    parser.add_argument("item_type", choices=ITEM_TYPES, nargs="?", default="all")
    parser.add_argument("--items-folder", default=os.getenv("MAGIC_RAMPAGE_ITEMS_DIR", DEFAULT_ITEMS_FOLDER))
    parser.add_argument("--enemy-dir", dest="enemy_dirs", action="append")
    parser.add_argument("--online-items-url", default=os.getenv("MAGIC_RAMPAGE_ITEMS_URL", DEFAULT_ONLINE_ITEMS_URL))
    parser.add_argument("--output-dir", default=os.getenv("MAGIC_RAMPAGE_OUTPUT_DIR", DEFAULT_OUTPUT_DIR))
    parser.add_argument("--log-level", default=os.getenv("MAGIC_RAMPAGE_LOG_LEVEL", "INFO"))
    args = parser.parse_args(argv)

    env_enemy_dirs = _split_env_paths(os.getenv("MAGIC_RAMPAGE_ENEMY_DIRS"))
    cli_enemy_dirs = tuple(Path(path) for path in args.enemy_dirs) if args.enemy_dirs else None
    enemy_dirs = cli_enemy_dirs or env_enemy_dirs or tuple(Path(path) for path in DEFAULT_ENEMY_DIRECTORIES)

    return AppConfig(
        output_type=args.output_type,
        item_type=args.item_type,
        items_folder=Path(args.items_folder),
        enemy_directories=enemy_dirs,
        online_items_url=args.online_items_url,
        output_dir=Path(args.output_dir),
        log_level=args.log_level.upper(),
    )


def configure_logging(level):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(levelname)s %(name)s: %(message)s",
    )
