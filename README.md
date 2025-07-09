This is a tool used for parsing items from the popular mobile and PC game "Magic Rampage". The tool aims to provide an overview of the current items in the game, which can be useful for Wiki editors, Youtubers and people who require this data for other needs.

## Setup & Usage

Recommended Python Version: 3.13 or newer

Recommended Platform: Visual Studio Code

```bash
pip install requests
```

Run the app with:

```bash
python main.py
```

There will be 8 output .txt folders, each containing the specific types of equipments. They are sorted based on maximum armor value for armors and rings and maximum damage value for the rest.

## Advanced Usage

The user can decide between **normal** and **developer** modes when executign the main.py:

```bash
python main.py normal
```

```bash
python main.py developer
```

If this is not specified, the program automatically assumes the **normal** mode. The difference between the modes is the readability. **normal** mode provides understandable textual representation of the item information. **developer** mode provides a list of items used for Magic Rampage Companion app. This automates all the heavy workload.

Apart from that the user can also define a second argument after the first:

```bash
python main.py normal all
```

```bash
python main.py normal axes
```

If the **all** mode is picked, the textual files for all item types will be made. If a specific item type is picked, then only that type will be produced. The possible types are: **all**, **enemy**, **class**,**armor**, **ring**, **sword**, **dagger**, **spear**, **hammer**, **axe** and **staff**. If none are picked, mode **all** is automatically assumed.