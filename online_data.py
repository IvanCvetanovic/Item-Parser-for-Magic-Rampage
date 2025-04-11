# online_data.py
import requests

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

    def index_online_data(self, online_data):
        online_index = {}
        for item in online_data:
            key = item.get("name", "").strip().lower()
            if key:
                online_index[key] = item
        print(f"[DEBUG] Indexed {len(online_index)} online items")
        return online_index

    def merge_online_fields(self, local_data, online_index):
        # Merge only fields that make sense per item type.
        for item_type in local_data:
            for item in local_data[item_type]:
                local_name = item.get("name", "").strip().lower()
                if local_name in online_index:
                    online_item = online_index[local_name]
                    if item_type == "armor":
                        if "maxLevelArmor" in online_item:
                            item["maxLevelArmor"] = online_item["maxLevelArmor"]
                        else:
                            print(f"[DEBUG] No maxLevelArmor found for {local_name} in type {item_type}")
                    elif item_type in ["sword", "hammer", "spear", "staff", "dagger", "axe"]:
                        if "maxLevelDamage" in online_item:
                            item["maxLevelDamage"] = online_item["maxLevelDamage"]
                        else:
                            print(f"[DEBUG] No maxLevelDamage found for {local_name} in type {item_type}")
                    else:
                        print(f"[DEBUG] Skipping merge for type {item_type} for {local_name}")
                else:
                    print(f"[DEBUG] Local item '{local_name}' not found in online index (type {item_type})")
        return local_data

    def convert_online_to_local(self, online_data):
        local_data = {
            "armor": [],
            "ring": [],
            "sword": [],
            "hammer": [],
            "spear": [],
            "staff": [],
            "dagger": [],
            "axe": []
        }
        for item in online_data:
            item_type_field = item.get("type", "").strip().lower()
            secondary = item.get("secondaryType", "").strip().lower()
            if item_type_field == "armor" or "maxLevelArmor" in item:
                target = "armor"
            elif item_type_field == "ring":
                target = "ring"
            elif item_type_field == "weapon":
                if secondary in ["sword"]:
                    target = "sword"
                elif secondary in ["spear"]:
                    target = "spear"
                elif secondary in ["staff"]:
                    target = "staff"
                elif secondary in ["dagger", "shuriken"]:
                    target = "dagger"
                elif secondary in ["hammer"]:
                    target = "hammer"
                elif secondary in ["axe"]:
                    target = "axe"
                else:
                    target = "sword"
            else:
                target = "ring"
            local_data[target].append(item)
        counts = ", ".join([f"{k}: {len(v)}" for k, v in local_data.items()])
        print(f"[DEBUG] Converted online data into local structure with counts: {counts}")
        return local_data
