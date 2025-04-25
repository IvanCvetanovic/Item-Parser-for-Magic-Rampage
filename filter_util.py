class DataFilter:
    def filter_parsed_data(self, local_data):
        for item_type in local_data:
            filtered_items = []
            for item in local_data[item_type]:
                raw_name = item.get("name", "").strip()
                # Exclude items whose name ends with " B"
                if raw_name.endswith(" B"):
                    print(f"[DEBUG] Excluding item '{raw_name}' because its name ends with ' B'")
                    continue
                # Exclude items with secondaryType equal to "essence", "rune", "key", or "arcane-rune"
                secondary = item.get("secondaryType", "").strip().lower()
                if secondary in {"essence", "rune", "key", "arcane-rune"}:
                    print(f"[DEBUG] Excluding item '{raw_name}' because its secondaryType is '{secondary}'")
                    continue

                sprite_val = item.get("sprite", "").strip().lower()
                if item_type == "armor":
                    if sprite_val == "armor_dummy.png":
                        print(f"[DEBUG] Excluding armor '{raw_name}' with sprite {sprite_val}")
                        continue
                elif item_type in ["sword", "hammer", "spear", "staff", "dagger", "axe"]:
                    if sprite_val == "sword_dummy.png" or sprite_val == "question_mark_entity.png":
                        print(f"[DEBUG] Excluding weapon '{raw_name}' with sprite {sprite_val}")
                        continue
                elif item_type == "ring":
                    if sprite_val in ["question_mark_entity.png", "ring_dummy.png"]:
                        print(f"[DEBUG] Excluding ring '{raw_name}' with sprite {sprite_val}")
                        continue
                filtered_items.append(item)
            local_data[item_type] = filtered_items
        return local_data
