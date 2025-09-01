import os
import re
import xml.etree.ElementTree as ET

STRINGS_FILE = "strings.xml"
LANG_DIR = "lang"
OUTPUT_BASE = "translations"
TARGET_LANGUAGES = ["de", "es", "fr", "it", "pt", "ru", "tr", "uk", "ja"]

TAGS_TO_PRESERVE = ["new-game-plus"]

def normalize_string(text):
    """
    Creates a generic template from a string for matching purposes.
    """
    cleaned_text = text.lower().strip().rstrip('.;').replace('\\%', '%')

    def replacer(match):
        number_part, tag_part = match.groups()
        
        if number_part:
            return "<ph>"
        
        if tag_part:
            tag_content = tag_part.strip("<>")
            if tag_content.startswith('number') or tag_content in TAGS_TO_PRESERVE:
                return "<ph>"
            else:
                return ""
        return ""

    pattern = r"([\d\.]+)|(<[^>]+>)"
    return re.sub(pattern, replacer, cleaned_text)

def parse_line(line):
    if '=' not in line or line.strip().startswith('#'): return None, None
    key, value = line.split('=', 1)
    key = key.strip().strip("'\"")
    value = value.strip().strip(";'\"")
    return key, value

def create_english_text_db(en_dir):
    print(f"📚 Building English text-to-key database...")
    db = {}
    for root, _, files in os.walk(en_dir):
        for fname in files:
            if fname.endswith(".strings"):
                with open(os.path.join(root, fname), "r", encoding="utf-8-sig") as f:
                    for line in f:
                        key, value = parse_line(line)
                        if key and value: db[normalize_string(value)] = (key, fname)
    print(f"   Found {len(db)} unique English text strings.")
    return db

def create_key_locations_map(en_dir):
    print(f"⚙️  Building English key-to-filename map...")
    key_map = {}
    for root, _, files in os.walk(en_dir):
        for fname in files:
            if fname.endswith(".strings"):
                with open(os.path.join(root, fname), "r", encoding="utf-8-sig") as f:
                    for line in f:
                        key, value = parse_line(line)
                        if key: key_map[key.lower()] = (key, fname)
    print(f"   Mapped {len(key_map)} unique English keys.")
    return key_map

def create_translations_db(lang_dir):
    print(f"🌍 Building translations database...")
    db = {}
    for root, _, files in os.walk(lang_dir):
        if os.path.samefile(root, lang_dir): continue
        for fname in files:
            if fname.endswith(".strings"):
                rel_path = os.path.relpath(root, lang_dir)
                lang_code = rel_path.split(os.sep)[0]
                if lang_code == 'en' or lang_code not in TARGET_LANGUAGES: continue
                db.setdefault(lang_code, {}).setdefault(fname, {})
                with open(os.path.join(root, fname), "r", encoding="utf-8-sig") as f:
                    for line in f:
                        key, value = parse_line(line)
                        if key: db[lang_code][fname][key.lower()] = value
    return db

def main():
    en_dir = os.path.join(LANG_DIR, 'en')
    key_locations = create_key_locations_map(en_dir)
    english_text_db = create_english_text_db(en_dir)
    translations_db = create_translations_db(LANG_DIR)

    try:
        tree = ET.parse(STRINGS_FILE)
        root = tree.getroot()
        xml_data = {}
        for s in root.findall("string"):
            name = s.attrib.get("name")
            if name:
                text = (s.text or "").strip().replace("\\'", "'")
                numbers_and_tags = re.findall(r"[\d\.]+|(<new-game-plus>)", text)
                xml_data[name] = {"text": text, "inject": numbers_and_tags}
    except FileNotFoundError:
        print(f"❌ ERROR: Main input file '{STRINGS_FILE}' not found. Exiting.")
        return

    os.makedirs(OUTPUT_BASE, exist_ok=True)
    writers = {lang: open(os.path.join(OUTPUT_BASE, f"values-{lang}", "strings.xml"), "w", encoding="utf-8") for lang in TARGET_LANGUAGES}
    for lang, writer in writers.items():
        os.makedirs(os.path.dirname(writer.name), exist_ok=True)
        writer.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n')
    
    unmatched_file_path = os.path.join(OUTPUT_BASE, "unmatched.xml")
    unmatched_writer = open(unmatched_file_path, "w", encoding="utf-8")
    unmatched_writer.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n')

    print("🗺️  Matching existing translations...")
    processed_strings = set()
    for string_name, data in xml_data.items():
        english_text = data["text"]
        source_key, source_filename = None, None
        
        normalized_english_text = normalize_string(english_text)

        if string_name.lower() in key_locations:
            source_key, source_filename = key_locations[string_name.lower()]
        elif normalized_english_text in english_text_db:
            source_key, source_filename = english_text_db[normalized_english_text]
        elif english_text.lower() in key_locations:
            source_key, source_filename = key_locations[english_text.lower()]
            
        if source_key and source_filename:
            processed_strings.add(string_name)
            for lang_code in TARGET_LANGUAGES:
                try:
                    translation_template = translations_db[lang_code][source_filename][source_key.lower()]

                    inject_iterator = iter(data["inject"])
                    translation_with_injects = re.sub(r"<[^>]+>", lambda m: next(inject_iterator, m.group()), translation_template)

                    def final_cleanup_replacer(match):
                        tag = match.group(0)
                        tag_content = tag.strip("<>")
                        if tag_content in TAGS_TO_PRESERVE:
                            return tag
                        else:
                            return ""
                    
                    translation_no_deco_tags = re.sub(r"<[^>]+>", final_cleanup_replacer, translation_with_injects)
                    
                    final_output_string = translation_no_deco_tags.replace(" .", " ").strip().replace("&", "&amp;").replace("'", "\\'").replace("%", "\\%")
                    
                    writers[lang_code].write(f'    <string name="{string_name}">{final_output_string}</string>\n')
                except KeyError:
                    pass

    print("📝 Writing unmatched strings to unmatched.xml...")
    unmatched_names = set(xml_data.keys()) - processed_strings
    for name in sorted(list(unmatched_names)):
        original_text = xml_data[name]["text"]
        original_text = original_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "\\'")
        unmatched_writer.write(f'    <string name="{name}">{original_text}</string>\n')
    
    for writer in writers.values():
        writer.write("</resources>\n"); writer.close()
    unmatched_writer.write("</resources>\n"); unmatched_writer.close()

    total_strings = len(xml_data)
    total_matched = len(processed_strings)
    total_unmatched = total_strings - total_matched
    print("\n" + "="*50)
    print("✅ Success! Processing complete.")
    print(f"   - Total Matched: {total_matched}")
    print(f"   - Unmatched (written to unmatched.xml): {total_unmatched}")
    print("="*50)

if __name__ == "__main__":
    main()