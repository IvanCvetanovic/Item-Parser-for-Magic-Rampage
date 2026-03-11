This project parses item, class, and enemy data from Magic Rampage and exports either readable text or developer-oriented constructor code.

## Requirements

- Python 3.11 or newer
- `requests`

Install dependencies with:

```bash
pip install .
```

## Usage

Default run:

```bash
python main.py
```

Explicit output and item type:

```bash
python main.py normal all
python main.py developer sword
python main.py developer enemy
```

You can override the default game paths:

```bash
python main.py normal all --items-folder "D:\SteamLibrary\steamapps\common\Magic Rampage\items"
python main.py developer enemy --enemy-dir "D:\SteamLibrary\steamapps\common\Magic Rampage\npcs\enemies" --enemy-dir "D:\SteamLibrary\steamapps\common\Magic Rampage\npcs\bosses"
python main.py normal all --output-dir custom-output
```

The same values can be provided through environment variables:

- `MAGIC_RAMPAGE_ITEMS_DIR`
- `MAGIC_RAMPAGE_ENEMY_DIRS`
- `MAGIC_RAMPAGE_ITEMS_URL`
- `MAGIC_RAMPAGE_OUTPUT_DIR`
- `MAGIC_RAMPAGE_LOG_LEVEL`

`MAGIC_RAMPAGE_ENEMY_DIRS` uses the platform path separator.

## Outputs

- `normal` mode exports readable text summaries.
- `developer` mode exports constructor lines for the companion app.
- Output files are written to `output/` by default.

Items are sorted deterministically:

- Armor by max armor, then name
- Rings by armor, then name
- Weapons by max damage, then name

## Architecture

- `pipeline.py` handles loading, filtering, merging, reclassification, and stable ordering.
- `exporters.py` handles writing text outputs.
- `models.py` provides typed records for items, classes, and enemies.
- `online_data.py` validates the online schema before use.

## Tests

Run the test suite with:

```bash
python -m unittest discover -s tests
```

## Language Getter

The language extraction tool remains separate:

```bash
python language_getter.py
```
