from parser import fetch_json_from_url, generate_armor_code

if __name__ == "__main__":
    # URL of the JSON file
    url = "https://gist.githubusercontent.com/andresan87/5670c559e5a930129aa03dfce7827306/raw"
    
    # Fetch JSON data
    json_data = fetch_json_from_url(url)
    
    if json_data is not None:
        armor_code = generate_armor_code(json_data)
        
        output_file = "armor_code.txt"
        with open(output_file, "w") as file:
            file.write("\n".join(armor_code))
        
        print(f"Armor code has been exported to {output_file}")
