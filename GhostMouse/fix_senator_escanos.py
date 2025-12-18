import os
import json
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraped_data_2021_senators")

def fix_json_files():
    print(f"Scanning directory: {DATA_DIR}")
    
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(".json"):
                filepath = os.path.join(root, file)
                print(f"Processing {filepath}...")
                
                with open(filepath, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        print(f"❌ Error decoding {file}")
                        continue
                
                modified = False
                
                # Data is a list of communes (regions in this case)
                if isinstance(data, list):
                    for entry in data:
                        if "commune" in entry and isinstance(entry["commune"], str):
                            original_name = entry["commune"]
                            # Regex to match trailing number
                            match = re.search(r"(\d+)$", original_name)
                            if match:
                                number = int(match.group(1))
                                # Remove number from name
                                new_name = original_name[:match.start()].strip()
                                
                                entry["commune"] = new_name
                                entry["escanos"] = number
                                modified = True
                                print(f"  Fixed: '{original_name}' -> '{new_name}', escanos: {number}")
                
                if modified:
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print("  ✅ Saved changes.")
                else:
                    print("  No changes needed.")

if __name__ == "__main__":
    fix_json_files()
