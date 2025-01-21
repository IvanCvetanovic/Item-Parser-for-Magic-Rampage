from parser import fetch_json_from_url, generate_armor_code, generate_ring_code

if __name__ == "__main__":
    url = "https://gist.githubusercontent.com/andresan87/5670c559e5a930129aa03dfce7827306/raw"
    
    json_data = fetch_json_from_url(url)
    
    if json_data is not None:
        # Generate and export armor code
        armor_code = generate_armor_code(json_data)
        with open("armor_code.txt", "w") as file:
            file.write("\n".join(armor_code))
        print("Armor code has been exported to armor_code.txt")
        
        # Generate and export ring code
        ring_code = generate_ring_code(json_data)
        with open("ring_code.txt", "w") as file:
            file.write("\n".join(ring_code))
        print("Ring code has been exported to ring_code.txt")
