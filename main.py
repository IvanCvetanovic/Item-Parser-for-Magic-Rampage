from armor_ring_parser import fetch_json_from_url, generate_armor_code, generate_ring_code
from weapon_parser import (
    generate_sword_code,
    generate_hammer_code,
    generate_spear_code,
    generate_staff_code,
    generate_dagger_code,
    generate_axe_code
)

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
        
        # Generate and export sword code
        sword_code = generate_sword_code(json_data)
        with open("sword_code.txt", "w") as file:
            file.write("\n".join(sword_code))
        print("Sword code has been exported to sword_code.txt")
        
        # Generate and export hammer code
        hammer_code = generate_hammer_code(json_data)
        with open("hammer_code.txt", "w") as file:
            file.write("\n".join(hammer_code))
        print("Hammer code has been exported to hammer_code.txt")
        
        # Generate and export spear code
        spear_code = generate_spear_code(json_data)
        with open("spear_code.txt", "w") as file:
            file.write("\n".join(spear_code))
        print("Spear code has been exported to spear_code.txt")
        
        # Generate and export staff code
        staff_code = generate_staff_code(json_data)
        with open("staff_code.txt", "w") as file:
            file.write("\n".join(staff_code))
        print("Staff code has been exported to staff_code.txt")
        
        # Generate and export dagger code
        dagger_code = generate_dagger_code(json_data)
        with open("dagger_code.txt", "w") as file:
            file.write("\n".join(dagger_code))
        print("Dagger code has been exported to dagger_code.txt")
        
        # Generate and export axe code
        axe_code = generate_axe_code(json_data)
        with open("axe_code.txt", "w") as file:
            file.write("\n".join(axe_code))
        print("Axe code has been exported to axe_code.txt")
