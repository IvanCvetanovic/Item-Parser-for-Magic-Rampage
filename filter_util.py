import logging

logger = logging.getLogger(__name__)


class DataFilter:
    def filter_parsed_data(self, local_data):
        """
        NOTE: This filter does NOT whitelist keys, so new price fields will not be dropped.
        """
        for item_type in local_data:
            filtered_items = []
            for item in local_data[item_type]:
                raw_name = item.get("name", "").strip()
                # Exclude items whose name ends with " B"
                if raw_name.endswith(" B"):
                    logger.debug("Excluding item %s because its name ends with ' B'", raw_name)
                    continue
                # Exclude items with secondaryType equal to "essence", "rune", "key", or "arcane-rune"
                secondary = item.get("secondaryType", "").strip().lower()
                if secondary in {"essence", "rune", "key", "arcane-rune"}:
                    logger.debug("Excluding item %s because its secondaryType is %s", raw_name, secondary)
                    continue

                sprite_val = item.get("sprite", "").strip().lower()
                if item_type == "armor":
                    if sprite_val == "armor_dummy.png":
                        logger.debug("Excluding armor %s with sprite %s", raw_name, sprite_val)
                        continue
                elif item_type in ["sword", "hammer", "spear", "staff", "dagger", "axe"]:
                    if sprite_val == "sword_dummy.png" or sprite_val == "question_mark_entity.png":
                        logger.debug("Excluding weapon %s with sprite %s", raw_name, sprite_val)
                        continue
                elif item_type == "ring":
                    if sprite_val in ["question_mark_entity.png", "ring_dummy.png"]:
                        logger.debug("Excluding ring %s with sprite %s", raw_name, sprite_val)
                        continue
                filtered_items.append(item)
            local_data[item_type] = filtered_items
        return local_data
