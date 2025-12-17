import json
import csv
import os

JSON_PATH = "/Users/nicolas/Desktop/PoliteiaDB/GhostMouse/presidential_2021.json"
CSV_PATH = "/Users/nicolas/Desktop/PoliteiaDB/GhostMouse/presidential_2021.csv"

def convert_to_csv():
    if not os.path.exists(JSON_PATH):
        print(f"Error: {JSON_PATH} not found.")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} regions from JSON.")

    # Flatten data
    rows = []
    for region in data:
        region_name = region["region_name"]
        region_id = region["region_id"]
        valid_votes = region["stats"]["valid_votes"]
        total_votes = region["stats"]["total_votes"]

        for cand in region["candidates"]:
            rows.append({
                "Region ID": region_id,
                "Region Name": region_name,
                "Candidate": cand["candidate"],
                "Party": cand["party"],
                "Votes": cand["votes"],
                "Percentage": cand["percentage"],
                "Total Valid Votes": valid_votes,
                "Total Regional Votes": total_votes
            })

    # Write CSV
    if not rows:
        print("No data to write.")
        return

    headers = rows[0].keys()
    
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Successfully created {CSV_PATH}")
    print(f"   Total Rows: {len(rows)}")

if __name__ == "__main__":
    convert_to_csv()
