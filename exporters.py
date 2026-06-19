import logging
from dataclasses import dataclass
from pathlib import Path
from armor_ring_parser import generate_armor_code, generate_ring_code
from weapon_parser import (
    generate_axe_code,
    generate_dagger_code,
    generate_hammer_code,
    generate_spear_code,
    generate_staff_code,
    generate_sword_code,
)
from class_parser import ClassParser
from enemy_parser import EnemyParser
from formatter import OutputFormatter

logger = logging.getLogger(__name__)

WEAPON_GENERATORS = {
    "sword": generate_sword_code,
    "hammer": generate_hammer_code,
    "spear": generate_spear_code,
    "staff": generate_staff_code,
    "dagger": generate_dagger_code,
    "axe": generate_axe_code,
}


@dataclass(frozen=True)
class ExportResult:
    label: str
    count: int
    path: Path | None  # None when content was printed to stdout instead of written


class ExportService:
    def __init__(self, output_dir, to_stdout=False):
        self.output_dir = Path(output_dir)
        self.to_stdout = to_stdout

    def _emit(self, filename, content):
        if self.to_stdout:
            print(f"# ==== {filename} ====")
            print(content)
            print()
            return None
        self.output_dir.mkdir(parents=True, exist_ok=True)
        out = self.output_dir / filename
        out.write_text(content, encoding="utf-8")
        logger.debug("Exported %s", out)
        return out

    def write_text(self, filename, content):
        """Write arbitrary text (e.g. a diff report), honoring --stdout."""
        return self._emit(filename, content)

    def export_items(self, items_by_type, item_type, output_type):
        items = items_by_type.get(item_type, [])
        if output_type == "developer":
            content = self._format_developer_items(item_type, items)
        else:
            content = self._format_normal_items(item_type, items)
        path = self._emit(f"{item_type}_code.txt", content)
        return ExportResult(item_type, len(items), path)

    def export_all_items(self, items_by_type, output_type):
        results = []
        for item_type, items in items_by_type.items():
            if not items:
                continue
            results.append(self.export_items(items_by_type, item_type, output_type))
        return results

    def export_classes(self, items_folder, output_type):
        class_file = Path(items_folder) / "class-heads.enml"
        parser = ClassParser(str(class_file))
        lines = parser.generate_class_code() if output_type == "developer" else parser.format_class_human()
        path = self._emit("class_code.txt", "\n".join(lines))
        return ExportResult("class", len(lines), path)

    def export_enemies(self, enemy_directories, output_type):
        parser = EnemyParser([str(path) for path in enemy_directories])
        lines = parser.parse_enemy_stats(mode=output_type)
        path = self._emit("enemy_code.txt", "\n".join(lines))
        return ExportResult("enemy", len(lines), path)

    @staticmethod
    def _format_developer_items(item_type, items):
        if item_type == "armor":
            return "\n".join(generate_armor_code(items))
        if item_type == "ring":
            return "\n".join(generate_ring_code(items))
        if item_type in WEAPON_GENERATORS:
            return "\n".join(WEAPON_GENERATORS[item_type](items))
        return ""

    @staticmethod
    def _format_normal_items(item_type, items):
        if item_type == "armor":
            return OutputFormatter.format_human_armor(items)
        if item_type == "ring":
            return OutputFormatter.format_human_ring(items)
        if item_type in WEAPON_GENERATORS:
            return OutputFormatter.format_human_weapon(items, default_weapon_type=item_type)
        return ""
