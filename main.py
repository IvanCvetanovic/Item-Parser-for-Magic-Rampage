import json
import requests

def fetch_json_from_url(url):
    """
    Fetches a JSON file from a URL and returns its contents as a Python object.

    :param url: URL to the JSON file
    :return: The data from the JSON file as a Python dictionary or list
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        data = response.json()  # Parse the JSON content
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def process_boost(value):
    """
    Converts boost values to the required format.
    If the value is 1, it is treated as 0.
    Otherwise, subtract 1 and multiply by 100.
    """
    return 0 if value == 1 else int((value - 1) * 100)

def generate_armor_code(data):
    """
    Generates a list of armor creation code for blocks with "type": "armor".

    :param data: JSON data as a Python object (list or dictionary)
    :return: A list of strings containing the generated armor code
    """
    armor_code_list = []

    if isinstance(data, list):
        for block in data:
            if isinstance(block, dict) and block.get("type") == "armor":
                # Extract fields or use defaults if missing
                name = block.get("name", "test_armor").replace(" ", "_").lower()
                frost = block.get("frost", False)
                min_armor = block.get("armor", 0)
                max_armor = block.get("maxLevelArmor", 0)
                upgrades = block.get("maxLevelAllowed", 0)

                # Boosts
                speed_boost = process_boost(block.get("speedBoost", 1))
                jump_boost = process_boost(block.get("jumpBoost", 1))
                magic_boost = process_boost(block.get("magicBoost", 1))
                sword_boost = process_boost(block.get("swordBoost", 1))
                staff_boost = process_boost(block.get("staffBoost", 1))
                dagger_boost = process_boost(block.get("daggerBoost", 1))
                axe_boost = process_boost(block.get("axeBoost", 1))
                hammer_boost = process_boost(block.get("hammerBoost", 1))
                spear_boost = process_boost(block.get("spearBoost", 1))

                # Generate the code string
                code = (
                    f"armorList.add(createArmor(R.string.{name}, Elements.NEUTRAL, "
                    f"{str(frost).lower()}, {min_armor}, {max_armor}, {upgrades}, "
                    f"{speed_boost}, {jump_boost}, {magic_boost}, {sword_boost}, "
                    f"{staff_boost}, {dagger_boost}, {axe_boost}, {hammer_boost}, "
                    f"{spear_boost}, R.drawable.armor_{name}));"
                )
                armor_code_list.append(code)
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                armor_code_list.extend(generate_armor_code(value))  # Recursive call

    return armor_code_list

# Main block to test the functions
if __name__ == "__main__":
    # URL of the JSON file
    url = "https://gist.githubusercontent.com/andresan87/5670c559e5a930129aa03dfce7827306/raw"
    
    # Fetch JSON data
    json_data = fetch_json_from_url(url)
    
    if json_data is not None:
        # Generate the armor code
        armor_code = generate_armor_code(json_data)
        
        # Write to a .txt file
        output_file = "armor_code.txt"
        with open(output_file, "w") as file:
            file.write("\n".join(armor_code))
        
        print(f"Armor code has been exported to {output_file}")
