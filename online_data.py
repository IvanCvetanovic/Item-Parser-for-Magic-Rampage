import re
import logging
import requests
import unicodedata
from models import PRICE_FIELD_NAMES

logger = logging.getLogger(__name__)

PRICE_FIELDS = PRICE_FIELD_NAMES

LOCAL_ITEM_TYPES = {"armor", "ring", "sword", "hammer", "spear", "staff", "dagger", "axe"}
ONLINE_REQUIRED_FIELDS = {"name", "type", "secondaryType"}


def _norm_key(s):
    """Normalize text for consistent matching."""
    s = (s or "").strip().lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s)
                if unicodedata.category(c) != 'Mn')
    s = re.sub(r"[^a-z0-9\s]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def _strip_type_suffix(name, item_type):
    """Remove the item type (e.g., 'hammer', 'sword') from the end of a name for better matching."""
    name = _norm_key(name)
    item_type = _norm_key(item_type)
    if name.endswith(" " + item_type):
        return name[:-(len(item_type) + 1)].strip()
    return name


def _matches(local_key, online_item, item_type):
    """Check if a local item name matches an online entry by any reasonable means."""
    candidates = [
        online_item.get("name_en"),
        online_item.get("name"),
    ]

    # include localized name_* variants
    for k, v in online_item.items():
        if k.startswith("name_"):
            candidates.append(v)

    # include sprite as last-resort identifier
    sprite = (online_item.get("sprite") or "").strip().lower()
    if sprite:
        candidates.append(sprite)

    # include stripped local name variant
    stripped = _strip_type_suffix(local_key, item_type)

    for c in candidates:
        norm_c = _norm_key(c)
        if norm_c in (local_key, stripped):
            return True
    return False


class OnlineDataManager:
    def get_online_item_data(self, url):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            valid_data = self.validate_online_item_data(data)
            logger.info("Retrieved %s valid item(s) from online JSON", len(valid_data))
            return valid_data
        except Exception as e:
            logger.warning("Error fetching online data: %s", e)
            return None

    def validate_online_item_data(self, data):
        valid_items = []
        for index, item in enumerate(data or []):
            missing = sorted(field for field in ONLINE_REQUIRED_FIELDS if field not in item)
            if missing:
                logger.warning("Skipping online item at index %s due to missing fields: %s", index, ", ".join(missing))
                continue
            valid_items.append(item)
        return valid_items

    def convert_online_to_local(self, online_data):
        """Convert online JSON items into the local grouped structure."""
        converted = {item_type: [] for item_type in LOCAL_ITEM_TYPES}

        for item in online_data:
            item_type = self._get_local_item_type(item)
            if item_type is None:
                continue
            converted[item_type].append(dict(item))

        return converted

    def _get_local_item_type(self, item):
        raw_type = _norm_key(item.get("type"))
        secondary = _norm_key(item.get("secondaryType"))

        if raw_type == "armor":
            return "armor"
        if raw_type == "ring" or secondary == "ring":
            return "ring"
        if raw_type == "weapon" and secondary in LOCAL_ITEM_TYPES:
            return secondary
        return None

    def merge_online_fields(self, local_data, online_data):
        """
        Merge selected online fields into locally parsed items.
        Lookup priority:
        - Try exact match (name_en / name)
        - Try stripped variant (without type suffix)
        - If still no match, retry with last word removed
        """
        for item_type in local_data:
            for item in local_data[item_type]:
                local_name_key = _norm_key(item.get("name", ""))
                match = None

                # Try normal matching
                for o in online_data:
                    if _matches(local_name_key, o, item_type):
                        match = o
                        break

                # Fallback: remove last word if not found
                if not match and " " in local_name_key:
                    reduced_key = " ".join(local_name_key.split(" ")[:-1])
                    for o in online_data:
                        if _matches(reduced_key, o, item_type):
                            match = o
                            break

                # Print only when no match found
                if not match:
                    logger.debug("Local item %s not found for type %s", item.get("name"), item_type)
                    continue

                # --- Merge data from online item ---
                if item_type == "armor":
                    if "maxLevelArmor" in match:
                        item["maxLevelArmor"] = match["maxLevelArmor"]
                elif item_type in ["sword", "hammer", "spear", "staff", "dagger", "axe"]:
                    if "maxLevelDamage" in match:
                        item["maxLevelDamage"] = match["maxLevelDamage"]

                # Copy price fields
                for key in PRICE_FIELDS:
                    if key in match:
                        item[key] = match[key]

        return local_data
