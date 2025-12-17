"""
Convert Region I JSON data to Politeia CSV format
Matches the schema used in RM folder
"""
import json
import csv
from datetime import datetime
import os

INPUT_FILE = "/Users/nicolas/Desktop/PoliteiaDB/II/region_ii_data.json"
OUTPUT_DIR = "/Users/nicolas/Desktop/PoliteiaDB/II"

# Load JSON data
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# ID counters
ids = {
    "jurisdiction": 1,
    "election": 1,
    "person": 1,
    "party": 1,
    "candidacy": 1,
    "office_term": 1,
    "party_membership": 1,
    "result": 1
}

# Caches for deduplication
cache_people = {}  # name -> id
cache_parties = {}  # party_name -> id
cache_jurisdictions = {}  # name -> id

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Initialize CSV files
csv_files = {}
csv_writers = {}

tables = {
    "wp_politeia_jurisdictions": ["id", "official_name", "common_name", "type", "parent_id", "external_code", "created_at", "updated_at"],
    "wp_politeia_elections": ["id", "office_id", "jurisdiction_id", "election_date", "created_at", "updated_at"],
    "wp_politeia_election_results": ["id", "election_id", "jurisdiction_id", "valid_votes", "blank_votes", "null_votes", "total_votes", "participation_rate", "created_at", "updated_at"],
    "wp_politeia_candidacies": ["id", "election_id", "person_id", "party_id", "votes", "vote_share", "elected", "created_at", "updated_at"],
    "wp_politeia_political_parties": ["id", "official_name", "short_name", "created_at", "updated_at"],
    "wp_politeia_party_memberships": ["id", "person_id", "party_id", "started_on", "created_at", "updated_at"],
    "wp_politeia_office_terms": ["id", "person_id", "office_id", "jurisdiction_id", "started_on", "status", "created_at", "updated_at"],
    "wp_politeia_people": ["id", "given_names", "paternal_surname", "created_at", "updated_at"]
}

for table, cols in tables.items():
    f = open(os.path.join(OUTPUT_DIR, f"{table}.csv"), "w", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    csv_files[table] = f
    csv_writers[table] = w

# Create Region II jurisdiction
region_name = "Región de Antofagasta"
region_id = ids["jurisdiction"]
ids["jurisdiction"] += 1

csv_writers["wp_politeia_jurisdictions"].writerow({
    "id": region_id,
    "official_name": region_name,
    "common_name": region_name,
    "type": "REGION",
    "parent_id": "",
    "external_code": "",
    "created_at": now(),
    "updated_at": now()
})

cache_jurisdictions[region_name] = region_id

OFFICE_ALCALDE = 1
ELECTION_DATE = "2024-10-27"
TERM_START_DATE = "2024-12-06"

# Process each commune
for commune_data in data:
    commune_name = commune_data['commune']
    
    # Create commune jurisdiction
    commune_id = ids["jurisdiction"]
    ids["jurisdiction"] += 1
    
    csv_writers["wp_politeia_jurisdictions"].writerow({
        "id": commune_id,
        "official_name": commune_name,
        "common_name": commune_name,
        "type": "COMMUNE",
        "parent_id": region_id,
        "external_code": "",  # We don't have external codes for Region I
        "created_at": now(),
        "updated_at": now()
    })
    
    cache_jurisdictions[commune_name] = commune_id
    
    # Create election
    election_id = ids["election"]
    ids["election"] += 1
    
    csv_writers["wp_politeia_elections"].writerow({
        "id": election_id,
        "office_id": OFFICE_ALCALDE,
        "jurisdiction_id": commune_id,
        "election_date": ELECTION_DATE,
        "created_at": now(),
        "updated_at": now()
    })
    
    # Create election results
    stats = commune_data['stats']
    csv_writers["wp_politeia_election_results"].writerow({
        "id": ids["result"],
        "election_id": election_id,
        "jurisdiction_id": commune_id,
        "valid_votes": stats['valid_votes'],
        "blank_votes": stats['blank_votes'],
        "null_votes": stats['null_votes'],
        "total_votes": stats['total_votes'],
        "participation_rate": stats['participation_rate'],
        "created_at": now(),
        "updated_at": now()
    })
    ids["result"] += 1
    
    # Process candidates
    for candidate in commune_data['candidates']:
        name = candidate['name']
        party_name = candidate['party']
        votes = candidate['votes']
        vote_share = candidate['percentage']
        elected = candidate['elected']
        
        # Get or create person
        if name not in cache_people:
            person_id = ids["person"]
            ids["person"] += 1
            
            # Split name
            parts = name.strip().split()
            if len(parts) >= 2:
                given = " ".join(parts[:-1])
                paternal = parts[-1]
            else:
                given = parts[0] if parts else "Unknown"
                paternal = ""
            
            csv_writers["wp_politeia_people"].writerow({
                "id": person_id,
                "given_names": given,
                "paternal_surname": paternal,
                "created_at": now(),
                "updated_at": now()
            })
            
            cache_people[name] = person_id
        else:
            person_id = cache_people[name]
        
        # Get or create party
        if party_name not in cache_parties:
            party_id = ids["party"]
            ids["party"] += 1
            
            # Extract short name (first word before -)
            short_name = ""
            if " - " in party_name:
                short_name = party_name.split(" - ")[0].strip()
            
            csv_writers["wp_politeia_political_parties"].writerow({
                "id": party_id,
                "official_name": party_name,
                "short_name": short_name,
                "created_at": now(),
                "updated_at": now()
            })
            
            cache_parties[party_name] = party_id
        else:
            party_id = cache_parties[party_name]
        
        # Create candidacy
        csv_writers["wp_politeia_candidacies"].writerow({
            "id": ids["candidacy"],
            "election_id": election_id,
            "person_id": person_id,
            "party_id": party_id,
            "votes": votes,
            "vote_share": vote_share,
            "elected": 1 if elected else 0,
            "created_at": now(),
            "updated_at": now()
        })
        ids["candidacy"] += 1
        
        # Create party membership
        csv_writers["wp_politeia_party_memberships"].writerow({
            "id": ids["party_membership"],
            "person_id": person_id,
            "party_id": party_id,
            "started_on": ELECTION_DATE,
            "created_at": now(),
            "updated_at": now()
        })
        ids["party_membership"] += 1
        
        # Create office term for elected candidate
        if elected:
            csv_writers["wp_politeia_office_terms"].writerow({
                "id": ids["office_term"],
                "person_id": person_id,
                "office_id": OFFICE_ALCALDE,
                "jurisdiction_id": commune_id,
                "started_on": TERM_START_DATE,
                "status": "ACTIVE",
                "created_at": now(),
                "updated_at": now()
            })
            ids["office_term"] += 1

# Close all files
for f in csv_files.values():
    f.close()

print("✓ Conversion complete!")
print(f"\nGenerated CSV files in: {OUTPUT_DIR}")
print(f"\nSummary:")
print(f"  Jurisdictions: {ids['jurisdiction'] - 1} (1 region + 7 communes)")
print(f"  Elections: {ids['election'] - 1}")
print(f"  People: {ids['person'] - 1}")
print(f"  Parties: {ids['party'] - 1}")
print(f"  Candidacies: {ids['candidacy'] - 1}")
print(f"  Party Memberships: {ids['party_membership'] - 1}")
print(f"  Office Terms: {ids['office_term'] - 1}")
print(f"  Election Results: {ids['result'] - 1}")
