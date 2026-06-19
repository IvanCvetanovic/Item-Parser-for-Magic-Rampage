import json
import logging
from pathlib import Path

from file_parser import FileParser
from filter_util import DataFilter
from online_data import OnlineDataManager
from pipeline import FILE_MAP

logger = logging.getLogger(__name__)


class DiffChecker:
    """Compare locally parsed ENML game files against the online gist.

    New  = item exists in game files but not in the gist (needs to be added).
    Removed = item is in the gist but not in game files (removed from game or parse mismatch).
    Changed = item exists in both but a stat from the ENML differs from the gist value.
    """

    def __init__(self, items_folder, online_items_url, file_map=None, data_filter=None, online_manager=None):
        self.items_folder = Path(items_folder)
        self.online_items_url = online_items_url
        self.file_map = file_map or FILE_MAP
        self.data_filter = data_filter or DataFilter()
        self.online_manager = online_manager or OnlineDataManager()

    def load_local(self):
        """Parse ENML files and return a name→item dict."""
        parsed = FileParser(str(self.items_folder), self.file_map).parse_files()
        filtered = self.data_filter.filter_parsed_data(parsed)
        flat = {}
        for items in filtered.values():
            for item in items:
                name = item.get("name")
                if name:
                    flat[name] = dict(item)
        return flat

    def load_online(self):
        """Fetch the gist and return a name→item dict."""
        raw = self.online_manager.get_online_item_data(self.online_items_url)
        if not raw:
            return {}
        return {item["name"]: item for item in raw if "name" in item}

    def compare(self, local, online):
        local_names = set(local)
        online_names = set(online)

        new_items = sorted(local_names - online_names, key=str.lower)
        removed_items = sorted(online_names - local_names, key=str.lower)

        changes = {}
        for name in sorted(local_names & online_names, key=str.lower):
            local_item = local[name]
            online_item = online[name]
            diffs = {}
            for key, local_val in local_item.items():
                if key == "name":
                    continue
                if key not in online_item:
                    continue
                online_val = online_item[key]
                if local_val != online_val:
                    diffs[key] = (online_val, local_val)
            if diffs:
                changes[name] = diffs

        return new_items, removed_items, changes

    def run(self):
        local = self.load_local()
        online = self.load_online()

        logger.info("Local ENML: %d items | Online gist: %d items", len(local), len(online))

        if not local:
            logger.warning("No items parsed from local ENML files — check your items folder path in Settings.")

        new_items, removed_items, changes = self.compare(local, online)
        return new_items, removed_items, changes, local

    @staticmethod
    def format_report(new_items, removed_items, changes, local):
        lines = []

        if new_items:
            lines.append(f"=== NEW ITEMS — in game, missing from gist ({len(new_items)}) ===")
            for name in new_items:
                item = local.get(name, {})
                secondary = item.get("secondaryType") or item.get("type", "?")
                lines.append(f"  + {name} [{secondary}]")
            lines.append("")

        if removed_items:
            lines.append(f"=== IN GIST ONLY — not found in local files ({len(removed_items)}) ===")
            for name in removed_items:
                lines.append(f"  - {name}")
            lines.append("")

        if changes:
            lines.append(f"=== STAT CHANGES — local differs from gist ({len(changes)}) ===")
            for name, diffs in sorted(changes.items(), key=lambda x: x[0].lower()):
                lines.append(f"  {name}:")
                for field, (online_val, local_val) in sorted(diffs.items()):
                    lines.append(f"    {field}: gist={online_val!r}  local={local_val!r}")
            lines.append("")

        if not new_items and not removed_items and not changes:
            lines.append("No changes detected.")
            lines.append("")

        lines.append(f"Summary: {len(new_items)} new, {len(removed_items)} gist-only, {len(changes)} stat changes.")
        return "\n".join(lines)
