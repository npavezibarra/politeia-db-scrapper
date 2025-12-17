import csv
import os

DATA_DIR = "/Users/nicolas/Desktop/PoliteiaDB/data"

REGIONS_TO_CHECK = [
    "Región de Tarapacá",
    "Región de Antofagasta",
    "Región de Atacama",
    "Región de Coquimbo",
    "Región de Valparaíso",
    "Región del Libertador General Bernardo O'Higgins",
    "Región del Maule",
    "Región del Biobío",
    "Región de la Araucanía",
    "Región de Los Lagos",
    "Región de Aysén del General Carlos Ibáñez del Campo",
    "Región de Magallanes y de la Antártica Chilena",
    "Región Metropolitana",
    "Región de Los Ríos",
    "Región de Arica y Parinacota",
    "Región de Ñuble"
]

def verify_data():
    jurisdictions_file = os.path.join(DATA_DIR, "wp_politeia_jurisdictions.csv")
    people_file = os.path.join(DATA_DIR, "wp_politeia_people.csv")
    elections_file = os.path.join(DATA_DIR, "wp_politeia_elections.csv")
    
    print("="*60)
    print("GLOBAL DATA VERIFICATION")
    print("="*60)
    
    # 1. Check Regions
    print("\n1. Checking Regions in wp_politeia_jurisdictions.csv:")
    found_regions = set()
    with open(jurisdictions_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if row[3] == 'REGION':
                found_regions.add(row[1])
    
    all_present = True
    for region in REGIONS_TO_CHECK:
        if region in found_regions:
            print(f"  ✓ Found: {region}")
        else:
            print(f"  ❌ MISSING: {region}")
            all_present = False
            
    if all_present:
        print("\n  ✅ All 16 regions are present!")
    else:
        print("\n  ⚠️ Some regions are missing!")

    # 2. Count Records
    print("\n2. Record Counts:")
    
    with open(people_file, 'r') as f:
        people_count = sum(1 for line in f) - 1
    print(f"  • People: {people_count} (Unique individuals)")
    
    with open(elections_file, 'r') as f:
        elections_count = sum(1 for line in f) - 1
    print(f"  • Elections: {elections_count} (Communes)")

    print("\n" + "="*60)

if __name__ == "__main__":
    verify_data()
