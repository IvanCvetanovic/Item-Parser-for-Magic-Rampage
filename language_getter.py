import os
import re
import xml.etree.ElementTree as ET

STRINGS_FILE = "strings.xml"
LANG_DIR = "lang"
OUTPUT_BASE = "translations"
TARGET_LANGUAGES = ["de", "es", "fr", "it", "pt", "ru", "tr", "uk", "ja"]

TAGS_TO_PRESERVE = ["new-game-plus"]

# -------- Key / text normalization helpers --------

def norm_key(k: str) -> str:
    """
    Normalize keys across packs:
    - lowercase
    - collapse '-' and '_' to a single underscore
    - trim spaces
    """
    if not k:
        return ""
    k = k.strip().lower()
    k = re.sub(r"[-_]+", "_", k)
    return k

def key_base_and_num(k: str):
    """
    Split normalized key into (base_without_trailing_digits, digits or None).
    e.g. 'skin_black_mage19' -> ('skin_black_mage', '19')
    """
    nk = norm_key(k)
    m = re.match(r"^(.*?)(\d+)$", nk)
    if m:
        return m.group(1), m.group(2)
    return nk, None

def normalize_string(text):
    """
    Creates a generic template from a string for matching purposes.
    Replaces numbers and certain tags with <ph>, drops other tags.
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
    if '=' not in line or line.strip().startswith('#'):
        return None, None
    key, value = line.split('=', 1)
    key = key.strip().strip("'\"")
    value = value.strip().strip(";'\"")
    return key, value

# -------- DB builders --------

def create_english_text_db(en_dir):
    print(f"📚 Building English text-to-key database...")
    db = {}  # normalized_english_text -> (orig_key, filename)
    for root, _, files in os.walk(en_dir):
        for fname in files:
            if fname.endswith(".strings"):
                with open(os.path.join(root, fname), "r", encoding="utf-8-sig") as f:
                    for line in f:
                        key, value = parse_line(line)
                        if key and value:
                            db[normalize_string(value)] = (key, fname)
    print(f"   Found {len(db)} unique English text strings.")
    return db

def create_key_locations_map(en_dir):
    print(f"⚙️  Building English key-to-filename map...")
    key_map = {}  # norm_key(key) -> (orig_key, filename)
    for root, _, files in os.walk(en_dir):
        for fname in files:
            if fname.endswith(".strings"):
                with open(os.path.join(root, fname), "r", encoding="utf-8-sig") as f:
                    for line in f:
                        key, _ = parse_line(line)
                        if key:
                            key_map[norm_key(key)] = (key, fname)
    print(f"   Mapped {len(key_map)} unique English keys.")
    return key_map

def create_translations_db(lang_dir):
    """
    Returns:
      - db: dict[lang_code][filename][norm_key] = value
      - index: dict[lang_code][norm_key] = (value, filename)  # filename-agnostic fallback
      - by_base: dict[lang_code][base] = {digits: (value, filename)}  # for numbered family lookup
    """
    print(f"🌍 Building translations database...")
    db = {}
    index = {}
    by_base = {}
    for root, _, files in os.walk(lang_dir):
        if os.path.samefile(root, lang_dir):
            continue
        for fname in files:
            if fname.endswith(".strings"):
                rel_path = os.path.relpath(root, lang_dir)
                lang_code = rel_path.split(os.sep)[0]
                if lang_code == 'en' or lang_code not in TARGET_LANGUAGES:
                    continue
                db.setdefault(lang_code, {}).setdefault(fname, {})
                index.setdefault(lang_code, {})
                by_base.setdefault(lang_code, {})
                with open(os.path.join(root, fname), "r", encoding="utf-8-sig") as f:
                    for line in f:
                        key, value = parse_line(line)
                        if key:
                            nk = norm_key(key)
                            db[lang_code][fname][nk] = value
                            # filename-agnostic (keep first seen)
                            index[lang_code].setdefault(nk, (value, fname))
                            base, digits = key_base_and_num(nk)
                            by_base[lang_code].setdefault(base, {})
                            if digits is not None and digits not in by_base[lang_code][base]:
                                by_base[lang_code][base][digits] = (value, fname)
    return db, index, by_base

# -------- Main processing --------

def main():
    en_dir = os.path.join(LANG_DIR, 'en')
    key_locations = create_key_locations_map(en_dir)
    english_text_db = create_english_text_db(en_dir)
    translations_db, translations_index, translations_by_base = create_translations_db(LANG_DIR)

    try:
        tree = ET.parse(STRINGS_FILE)
        root = tree.getroot()
        xml_data = {}
        for s in root.findall("string"):
            name = s.attrib.get("name")
            if name:
                text = (s.text or "").strip().replace("\\'", "'")
                # Capture numbers and specific tags we want to inject back
                numbers_and_tags = re.findall(r"[\d\.]+|(<new-game-plus>)", text)
                xml_data[name] = {"text": text, "inject": numbers_and_tags}
    except FileNotFoundError:
        print(f"❌ ERROR: Main input file '{STRINGS_FILE}' not found. Exiting.")
        return

    os.makedirs(OUTPUT_BASE, exist_ok=True)

    # Ensure per-language output directories exist BEFORE opening files
    writers = {}
    for lang in TARGET_LANGUAGES:
        dir_path = os.path.join(OUTPUT_BASE, f"values-{lang}")
        os.makedirs(dir_path, exist_ok=True)
        fpath = os.path.join(dir_path, "strings.xml")
        writer = open(fpath, "w", encoding="utf-8")
        writer.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n')
        writers[lang] = writer

    unmatched_file_path = os.path.join(OUTPUT_BASE, "unmatched.xml")
    unmatched_writer = open(unmatched_file_path, "w", encoding="utf-8")
    unmatched_writer.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n')

    print("🗺️  Matching existing translations...")
    processed_strings = set()

    for string_name, data in xml_data.items():
        english_text = data["text"]
        normalized_english_text = normalize_string(english_text)

        source_key_orig, source_filename = None, None

        # 1) Prefer match by key in English pack (normalize key!)
        target_key_norm = norm_key(string_name)
        if target_key_norm in key_locations:
            source_key_orig, source_filename = key_locations[target_key_norm]
        # 2) Otherwise, match by English normalized text present in English .strings
        elif normalized_english_text in english_text_db:
            source_key_orig, source_filename = english_text_db[normalized_english_text]

        # We will try multiple candidate keys when fetching per-language translations
        candidate_keys = []
        # Always try the actual target key first (handles "18 vs 19" differences across locales)
        candidate_keys.append(target_key_norm)
        if source_key_orig:
            candidate_keys.append(norm_key(source_key_orig))

        # Base-key fallback: if key ends with digits, try any member of that numbered family
        base, digits = key_base_and_num(target_key_norm)

        found_any_lang = False
        for lang_code in TARGET_LANGUAGES:
            translation_template = None

            # A) Direct target-key lookup (filename-agnostic)
            for ck in candidate_keys:
                if lang_code in translations_index and ck in translations_index[lang_code]:
                    translation_template, _fname = translations_index[lang_code][ck]
                    break

            # B) If we have an English anchor and a filename, prefer same-file+source_key
            if translation_template is None and source_key_orig and source_filename:
                skn = norm_key(source_key_orig)
                if (lang_code in translations_db and
                    source_filename in translations_db[lang_code] and
                    skn in translations_db[lang_code][source_filename]):
                    translation_template = translations_db[lang_code][source_filename][skn]

            # C) If still nothing, try same source_key anywhere (filename-agnostic)
            if translation_template is None and source_key_orig:
                skn = norm_key(source_key_orig)
                if lang_code in translations_index and skn in translations_index[lang_code]:
                    translation_template, _fname = translations_index[lang_code][skn]

            # D) Base-key family fallback: accept any digits under same base (e.g., 18 -> 19)
            if translation_template is None and lang_code in translations_by_base and base in translations_by_base[lang_code]:
                # Prefer exact digits if present; otherwise pick any (sorted for determinism)
                family = translations_by_base[lang_code][base]
                if digits and digits in family:
                    translation_template, _fname = family[digits]
                else:
                    # pick the highest number to be stable (or first sorted)
                    for d in sorted(family.keys(), key=lambda x: int(x)):
                        translation_template, _fname = family[d]
                        break

            if translation_template is None:
                continue  # no translation in this language; try next language

            found_any_lang = True

            # Re-inject preserved numbers/tags into placeholder positions
            inject_iterator = iter(data["inject"])
            translation_with_injects = re.sub(
                r"<[^>]+>",
                lambda m: next(inject_iterator, m.group()),
                translation_template
            )

            # Final cleanup: drop decoration tags except those we want to keep
            def final_cleanup_replacer(match):
                tag = match.group(0)
                tag_content = tag.strip("<>")
                if tag_content in TAGS_TO_PRESERVE:
                    return tag
                else:
                    return ""

            translation_no_deco_tags = re.sub(
                r"<[^>]+>", final_cleanup_replacer, translation_with_injects
            )

            final_output_string = (
                translation_no_deco_tags
                .replace(" .", " ")
                .strip()
                .replace("&", "&amp;")
                .replace("'", "\\'")
                .replace("%", "\\%")
            )

            writers[lang_code].write(
                f'    <string name="{string_name}">{final_output_string}</string>\n'
            )

        if found_any_lang:
            processed_strings.add(string_name)

    print("📝 Writing unmatched strings to unmatched.xml...")
    unmatched_names = set(xml_data.keys()) - processed_strings
    for name in sorted(list(unmatched_names)):
        original_text = xml_data[name]["text"]
        original_text = (original_text
                         .replace("&", "&amp;")
                         .replace("<", "&lt;")
                         .replace(">", "&gt;")
                         .replace("'", "\\'"))
        unmatched_writer.write(
            f'    <string name="{name}">{original_text}</string>\n'
        )

    for writer in writers.values():
        writer.write("</resources>\n")
        writer.close()
    unmatched_writer.write("</resources>\n")
    unmatched_writer.close()

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
