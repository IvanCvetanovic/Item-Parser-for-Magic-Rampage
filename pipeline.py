import logging
from file_parser import FileParser
from online_data import OnlineDataManager
from filter_util import DataFilter
from models import ItemRecord, OUTPUT_ORDER

logger = logging.getLogger(__name__)

FILE_MAP = {
    "special-armors.enml": "armor",
    "armor-cloth-1.enml": "armor",
    "armor-leather-1.enml": "armor",
    "armor-plate-1.enml": "armor",
    "special-items.enml": "ring",
    "special-swords.enml": "sword",
    "weapon-sword-1.enml": "sword",
    "special-spears.enml": "spear",
    "special-staves.enml": "staff",
    "weapon-staff-1.enml": "staff",
    "special-hammers.enml": "hammer",
    "special-daggers.enml": "dagger",
    "special-shurikens.enml": "dagger",
    "weapon-dagger-1.enml": "dagger",
    "special-grimoires.enml": "staff",
    "special-axes.enml": "axe",
    "weapon-axe-1.enml": "axe",
    "weapon-axe-2.enml": "axe",
}


class ItemPipeline:
    def __init__(self, items_folder, online_items_url, file_map=None, data_filter=None, online_manager=None):
        self.items_folder = items_folder
        self.online_items_url = online_items_url
        self.file_map = file_map or FILE_MAP
        self.data_filter = data_filter or DataFilter()
        self.online_manager = online_manager or OnlineDataManager()

    def load_items(self):
        local = FileParser(str(self.items_folder), self.file_map).parse_files()
        total = sum(len(items) for items in local.values())
        online = self.online_manager.get_online_item_data(self.online_items_url)

        if total == 0:
            if online:
                logger.info("No local items found. Using online fallback data.")
                merged = self.online_manager.convert_online_to_local(online)
            else:
                logger.warning("No local items found and online fallback is unavailable.")
                merged = local
        elif online:
            merged = self.online_manager.merge_online_fields(local, online)
        else:
            merged = local

        filtered = self.data_filter.filter_parsed_data(merged)
        reclassified = self.reclassify_axes_and_hammers(filtered)
        return self.to_records(self.sort_grouped_items(reclassified))

    @staticmethod
    def reclassify_axes_and_hammers(data):
        axe_blocks = data.get("axe", [])
        to_move = [
            block for block in axe_blocks
            if str(block.get("secondaryType", "")).lower() in ("mace", "hammer")
        ]
        if to_move:
            data["axe"] = [block for block in axe_blocks if block not in to_move]
            data["hammer"] = data.get("hammer", []) + to_move
        return data

    @staticmethod
    def sort_grouped_items(data):
        sorted_data = {}
        for item_type, items in data.items():
            records = [ItemRecord.from_mapping(item_type, item) for item in items]
            sorted_data[item_type] = sorted(records, key=lambda record: record.sort_key())
        return sorted_data

    @staticmethod
    def to_records(data):
        ordered = {}
        for item_type in OUTPUT_ORDER:
            ordered[item_type] = list(data.get(item_type, []))
        for item_type, items in data.items():
            if item_type not in ordered:
                ordered[item_type] = list(items)
        return ordered
