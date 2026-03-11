import os
import logging
from parser_utils import parse_scalar

logger = logging.getLogger(__name__)

class FileParser:
    def __init__(self, folder_path, file_to_type):
        self.folder_path = folder_path
        self.file_to_type = file_to_type

    def parse_enml_block(self, block_text):
        """Convert a single item block to a dictionary, ignoring inline comments."""
        item = {}
        for line in block_text.strip().splitlines():
            # Remove inline comments (everything after '//')
            if '//' in line:
                line = line.split('//')[0]
            line = line.strip()
            if "=" in line:
                try:
                    key, value = line.split("=", 1)
                except Exception as e:
                    logger.warning("Malformed line: %s", e)
                    continue
                key = key.strip()
                item[key] = parse_scalar(value)
        return item

    def parse_files(self):
        """Parse all ENML files in the folder using the file_to_type mapping."""
        parsed_data = {v: [] for v in set(self.file_to_type.values())}
        if not os.path.exists(self.folder_path):
            logger.debug("Local directory not found: %s", self.folder_path)
            return parsed_data

        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".enml") and file_name in self.file_to_type:
                logger.debug("Found relevant file: %s", file_name)
                item_type = self.file_to_type[file_name]
                file_path = os.path.join(self.folder_path, file_name)
                with open(file_path, "r", encoding="utf-8") as file:
                    lines = file.readlines()

                block_lines = []
                inside_block = False
                pending_item = False
                brace_depth = 0

                for line in lines:
                    line_stripped = line.strip()
                    if line_stripped.lower().startswith("item"):
                        pending_item = True
                        continue

                    if pending_item and "{" in line_stripped:
                        inside_block = True
                        pending_item = False
                        brace_depth = 1
                        block_lines = [line_stripped[line_stripped.index("{") + 1:]]
                        continue

                    if inside_block:
                        if "{" in line_stripped:
                            brace_depth += 1
                        if "}" in line_stripped:
                            brace_depth -= 1
                            if brace_depth == 0:
                                inside_block = False
                                block_text = "\n".join(block_lines)
                                item_data = self.parse_enml_block(block_text)
                                if item_data:
                                    parsed_data[item_type].append(item_data)
                                block_lines = []
                                continue
                        block_lines.append(line_stripped)
                logger.info("Parsed %s %s item(s) from %s", len(parsed_data[item_type]), item_type, file_name)
        return parsed_data
