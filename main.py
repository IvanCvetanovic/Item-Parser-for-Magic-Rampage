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

def find_secondary_type_plate(data):
    """
    Searches for blocks in the JSON data containing "secondaryType": "plate".

    :param data: JSON data as a Python object (list or dictionary)
    """
    if isinstance(data, list):
        for block in data:
            if isinstance(block, dict) and block.get("secondaryType") == "plate":
                print("Item found")
    elif isinstance(data, dict):
        for key, value in data.items():
            if key == "secondaryType" and value == "plate":
                print("Item found")
            elif isinstance(value, (list, dict)):
                find_secondary_type_plate(value)  # Recursive call for nested structures

# Main block to test the functions
if __name__ == "__main__":
    # URL of the JSON file
    url = "https://gist.githubusercontent.com/andresan87/5670c559e5a930129aa03dfce7827306/raw"
    
    # Fetch JSON data
    json_data = fetch_json_from_url(url)
    
    # Search for "secondaryType": "plate"
    if json_data is not None:
        find_secondary_type_plate(json_data)
