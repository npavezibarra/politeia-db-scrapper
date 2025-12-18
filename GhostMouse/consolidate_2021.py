"""
2021 Presidential Election Data Consolidation Script
Consolidates JSON data from regions into the master CSV files.
"""
import json
import csv
import os
from datetime import datetime

# Resolve paths relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# CSV Tables and Columns (Same schema as merge_regions.py)
TABLES = {
    "wp_politeia_jurisdictions": ["id", "official_name", "common_name", "type", "parent_id", "external_code", "created_at", "updated_at"],
    "wp_politeia_elections": ["id", "office_id", "jurisdiction_id", "election_date", "created_at", "updated_at"],
    "wp_politeia_election_results": ["id", "election_id", "jurisdiction_id", "valid_votes", "blank_votes", "null_votes", "total_votes", "participation_rate", "created_at", "updated_at"],
    "wp_politeia_candidacies": ["id", "election_id", "person_id", "party_id", "votes", "vote_share", "elected", "created_at", "updated_at"],
    "wp_politeia_political_parties": ["id", "official_name", "short_name", "created_at", "updated_at"],
    "wp_politeia_party_memberships": ["id", "person_id", "party_id", "started_on", "created_at", "updated_at"],
    "wp_politeia_office_terms": ["id", "person_id", "office_id", "jurisdiction_id", "started_on", "status", "created_at", "updated_at"],
    "wp_politeia_people": ["id", "given_names", "paternal_surname", "created_at", "updated_at"]
}

OFFICE_PRESIDENTE = 2
ELECTION_DATE = "2021-11-21"
TERM_START_DATE = "2022-03-11"

# Region Code to Name Mapping (for creating Jurisdictions if missing)
REGION_NAMES = {
    "XV": "Región de Arica y Parinacota",
    "I": "Región de Tarapacá",
    "II": "Región de Antofagasta",
    "III": "Región de Atacama",
    "IV": "Región de Coquimbo",
    "V": "Región de Valparaíso",
    "RM": "Región Metropolitana de Santiago",
    "VI": "Región del Libertador General Bernardo O'Higgins",
    "VII": "Región del Maule",
    "XVI": "Región de Ñuble",
    "VIII": "Región del Biobío",
    "IX": "Región de la Araucanía",
    "XIV": "Región de Los Ríos",
    "X": "Región de Los Lagos",
    "XI": "Región de Aysén del General Carlos Ibáñez del Campo",
    "XII": "Región de Magallanes y de la Antártica Chilena"
}

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Merger:
    def __init__(self):
        self.ids = {}
        self.cache_people = {}  # "Given Paternal" -> id
        self.cache_parties = {} # "Party Name" -> id
        self.cache_jurisdictions = {} # "Name" -> id
        self.writers = {}
        self.files = {}
        
    def load_current_state(self):
        print(f"Loading current state from {DATA_DIR}...")
        
        if not os.path.exists(DATA_DIR):
            print(f"Creating data directory: {DATA_DIR}")
            os.makedirs(DATA_DIR)

        # 1. Load Max IDs and Caches
        for table in TABLES:
            file_path = os.path.join(DATA_DIR, f"{table}.csv")
            max_id = 0
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Update Max ID
                        if row['id']:
                            curr_id = int(row['id'])
                            if curr_id > max_id:
                                max_id = curr_id
                            
                        # Populate Caches
                        if table == "wp_politeia_people":
                            full_name = f"{row['given_names']} {row['paternal_surname']}".strip()
                            self.cache_people[full_name] = curr_id
                            
                        elif table == "wp_politeia_political_parties":
                            self.cache_parties[row['official_name']] = curr_id
                            
                        elif table == "wp_politeia_jurisdictions":
                            self.cache_jurisdictions[row['official_name']] = curr_id
                            
            self.ids[table] = max_id + 1
            print(f"  {table}: Next ID {self.ids[table]}")

    def open_append_writers(self):
        for table, cols in TABLES.items():
            file_path = os.path.join(DATA_DIR, f"{table}.csv")
            # If file doesn't exist, write header
            file_exists = os.path.exists(file_path)
            
            f = open(file_path, "a", newline="", encoding="utf-8")
            w = csv.DictWriter(f, fieldnames=cols)
            
            if not file_exists:
                w.writeheader()
                
            self.files[table] = f
            self.writers[table] = w

    def close(self):
        for f in self.files.values():
            f.close()

    def merge_region(self, json_file, region_name):
        print(f"\nMerging {os.path.basename(json_file)}...")
        
        if not os.path.exists(json_file):
            print(f"  ⚠️ File not found: {json_file}")
            return

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 1. Ensure Region Jurisdiction
        if region_name in self.cache_jurisdictions:
            region_id = self.cache_jurisdictions[region_name]
        else:
            region_id = self.ids["wp_politeia_jurisdictions"]
            self.writers["wp_politeia_jurisdictions"].writerow({
                "id": region_id,
                "official_name": region_name,
                "common_name": region_name,
                "type": "REGION",
                "parent_id": "",
                "external_code": "",
                "created_at": now(),
                "updated_at": now()
            })
            self.cache_jurisdictions[region_name] = region_id
            self.ids["wp_politeia_jurisdictions"] += 1
            print(f"  Created Region: {region_name} (ID {region_id})")

        # 2. Process Communes
        for commune_data in data:
            commune_name = commune_data['commune']
            
            # Jurisdiction (Commune)
            if commune_name in self.cache_jurisdictions:
                commune_id = self.cache_jurisdictions[commune_name]
            else:
                commune_id = self.ids["wp_politeia_jurisdictions"]
                self.writers["wp_politeia_jurisdictions"].writerow({
                    "id": commune_id,
                    "official_name": commune_name,
                    "common_name": commune_name,
                    "type": "COMMUNE",
                    "parent_id": region_id,
                    "external_code": "",
                    "created_at": now(),
                    "updated_at": now()
                })
                self.cache_jurisdictions[commune_name] = commune_id
                self.ids["wp_politeia_jurisdictions"] += 1
            
            # Election
            election_id = self.ids["wp_politeia_elections"]
            self.writers["wp_politeia_elections"].writerow({
                "id": election_id,
                "office_id": OFFICE_PRESIDENTE,
                "jurisdiction_id": commune_id,
                "election_date": ELECTION_DATE,
                "created_at": now(),
                "updated_at": now()
            })
            self.ids["wp_politeia_elections"] += 1
            
            # Results
            stats = commune_data['stats']
            self.writers["wp_politeia_election_results"].writerow({
                "id": self.ids["wp_politeia_election_results"],
                "election_id": election_id,
                "jurisdiction_id": commune_id,
                "valid_votes": stats.get('valid_votes', 0),
                "blank_votes": stats.get('blank_votes', 0),
                "null_votes": stats.get('null_votes', 0),
                "total_votes": stats.get('total_votes', 0),
                "participation_rate": stats.get('participation_rate', 0),
                "created_at": now(),
                "updated_at": now()
            })
            self.ids["wp_politeia_election_results"] += 1
            
            # Candidates
            for cand in commune_data['candidates']:
                name = cand['name']
                party_name = cand['party']
                
                # Person
                if name in self.cache_people:
                    person_id = self.cache_people[name]
                else:
                    person_id = self.ids["wp_politeia_people"]
                    parts = name.strip().split()
                    if len(parts) >= 2:
                        given = " ".join(parts[:-1])
                        paternal = parts[-1]
                    else:
                        given = parts[0] if parts else "Unknown"
                        paternal = ""
                        
                    self.writers["wp_politeia_people"].writerow({
                        "id": person_id,
                        "given_names": given,
                        "paternal_surname": paternal,
                        "created_at": now(),
                        "updated_at": now()
                    })
                    self.cache_people[name] = person_id
                    self.ids["wp_politeia_people"] += 1
                    
                # Party
                if party_name in self.cache_parties:
                    party_id = self.cache_parties[party_name]
                else:
                    party_id = self.ids["wp_politeia_political_parties"]
                    short = party_name.split(" - ")[0].strip() if " - " in party_name else ""
                    
                    self.writers["wp_politeia_political_parties"].writerow({
                        "id": party_id,
                        "official_name": party_name,
                        "short_name": short,
                        "created_at": now(),
                        "updated_at": now()
                    })
                    self.cache_parties[party_name] = party_id
                    self.ids["wp_politeia_political_parties"] += 1
                    
                # Candidacy
                self.writers["wp_politeia_candidacies"].writerow({
                    "id": self.ids["wp_politeia_candidacies"],
                    "election_id": election_id,
                    "person_id": person_id,
                    "party_id": party_id,
                    "votes": cand['votes'],
                    "vote_share": cand['percentage'],
                    "elected": 1 if cand['elected'] else 0,
                    "created_at": now(),
                    "updated_at": now()
                })
                self.ids["wp_politeia_candidacies"] += 1
                
                # Membership
                self.writers["wp_politeia_party_memberships"].writerow({
                    "id": self.ids["wp_politeia_party_memberships"],
                    "person_id": person_id,
                    "party_id": party_id,
                    "started_on": ELECTION_DATE,
                    "created_at": now(),
                    "updated_at": now()
                })
                self.ids["wp_politeia_party_memberships"] += 1
                
                # Office Term
                if cand['elected']:
                    self.writers["wp_politeia_office_terms"].writerow({
                        "id": self.ids["wp_politeia_office_terms"],
                        "person_id": person_id,
                        "office_id": OFFICE_PRESIDENTE,
                        "jurisdiction_id": commune_id,
                        "started_on": TERM_START_DATE,
                        "status": "ACTIVE",
                        "created_at": now(),
                        "updated_at": now()
                    })
                    self.ids["wp_politeia_office_terms"] += 1
        
        print(f"✓ Merged {len(data)} communes from {region_name}")

if __name__ == "__main__":
    merger = Merger()
    merger.load_current_state()
    merger.open_append_writers()
    
    # Iterate through all configured regions
    for code, name in REGION_NAMES.items():
        # Construct path: BASE_DIR / GhostMouse / scraped_data_2021_presidentes / CODE / region_{code}_data.json
        # BASE_DIR is root of politeia-db-scrapper
        # So BASE_DIR/GhostMouse/scraped_data_2021_presidentes...
        
        json_filename = f"region_{code.lower()}_data.json"
        
        # NOTE: BASE_DIR in this script was defined as os.path.dirname(script_dir)
        # script_dir is GhostMouse
        # so BASE_DIR is project root
        
        json_path = os.path.join(BASE_DIR, "GhostMouse", "scraped_data_2021_presidentes", code, json_filename)
        
        merger.merge_region(json_path, name)
        
    merger.close()
    print("\n✓ All available 2021 data merged into master CSVs!")
