import re
import requests
import unicodedata

PRICE_FIELDS = [
    "freemiumGoldPrice", "premiumGoldPrice",
    "freemiumCoinPrice", "premiumCoinPrice",
    "baseFreemiumSellPrice", "basePremiumSellPrice"
]


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
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            print(f"[DEBUG] Retrieved {len(data)} items from online JSON")
            return data
        except Exception as e:
            print(f"Error fetching online data: {e}")
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
                sprite = (item.get("sprite") or "").strip().lower()
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
                    print(f"[DEBUG] Local item '{item.get('name')}' not found (type {item_type})")
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
