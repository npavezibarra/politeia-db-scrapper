import json
import csv
import os
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SOURCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraped_data_2021_senators")

# Constants
OFFICE_SENATOR = 3
ELECTION_DATE = "2021-11-21"
TERM_START_DATE = "2022-03-11"

# Tables
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

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class SenatorMerger:
    def __init__(self):
        self.ids = {}
        self.cache_people = {}  # "Given Paternal" -> id
        self.cache_parties = {} # "Party Name" -> id
        self.cache_jurisdictions = {} # "Name" -> id
        self.writers = {}
        self.files = {}

    def load_state(self):
        print("Loading current DB state...")
        for table in TABLES:
            file_path = os.path.join(DATA_DIR, f"{table}.csv")
            max_id = 0
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        curr_id = int(row['id'])
                        if curr_id > max_id:
                            max_id = curr_id
                        
                        # Populate caches
                        if table == "wp_politeia_people":
                            full = f"{row['given_names']} {row['paternal_surname']}".strip()
                            self.cache_people[full] = curr_id
                        elif table == "wp_politeia_political_parties":
                            self.cache_parties[row['official_name']] = curr_id
                        elif table == "wp_politeia_jurisdictions":
                            self.cache_jurisdictions[row['official_name']] = curr_id
            
            self.ids[table] = max_id + 1
            print(f"  {table}: next_id={self.ids[table]}")

    def open_writers(self):
        for table, cols in TABLES.items():
            f = open(os.path.join(DATA_DIR, f"{table}.csv"), "a", newline="", encoding="utf-8")
            w = csv.DictWriter(f, fieldnames=cols)
            self.files[table] = f
            self.writers[table] = w

    def close_writers(self):
        for f in self.files.values():
            f.close()

    def process_directory(self):
        print(f"Scanning {SOURCE_DIR}...")
        for root, dirs, files in os.walk(SOURCE_DIR):
            for file in files:
                if file.endswith("_data.json"):
                    path = os.path.join(root, file)
                    self.process_file(path)

    def process_file(self, json_path):
        print(f"\nProcessing {os.path.basename(json_path)}...")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle list structure (some files might be wrapped in list)
        if isinstance(data, list):
            data = data[0]

        region_name = data.get('commune') # mapped to region name in previous steps
        if not region_name:
            print("  ❌ Skipping: No 'commune/region' name found")
            return

        # 1. Resolve Jurisdiction (Region)
        if region_name in self.cache_jurisdictions:
            region_id = self.cache_jurisdictions[region_name]
        else:
            # Create Region if not exists (unlikely given previous scraping)
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

        # 2. Create Election (Senator for this Region)
        election_id = self.ids["wp_politeia_elections"]
        self.writers["wp_politeia_elections"].writerow({
            "id": election_id,
            "office_id": OFFICE_SENATOR,
            "jurisdiction_id": region_id,
            "election_date": ELECTION_DATE,
            "created_at": now(),
            "updated_at": now()
        })
        self.ids["wp_politeia_elections"] += 1
        print(f"  Created Election ID {election_id} for {region_name}")

        # 3. Create Results (Stats)
        stats = data.get('stats', {})
        self.writers["wp_politeia_election_results"].writerow({
            "id": self.ids["wp_politeia_election_results"],
            "election_id": election_id,
            "jurisdiction_id": region_id,
            "valid_votes": stats.get('valid_votes', 0),
            "blank_votes": stats.get('blank_votes', 0),
            "null_votes": stats.get('null_votes', 0),
            "total_votes": stats.get('total_votes', 0),
            "participation_rate": stats.get('participation_rate', 0),
            "created_at": now(),
            "updated_at": now()
        })
        self.ids["wp_politeia_election_results"] += 1

        # 4. Process Candidates
        candidates = data.get('candidates', [])
        for cand in candidates:
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

            # Office Term (if elected)
            if cand['elected']:
                self.writers["wp_politeia_office_terms"].writerow({
                    "id": self.ids["wp_politeia_office_terms"],
                    "person_id": person_id,
                    "office_id": OFFICE_SENATOR,
                    "jurisdiction_id": region_id,
                    "started_on": TERM_START_DATE,
                    "status": "ACTIVE",
                    "created_at": now(),
                    "updated_at": now()
                })
                self.ids["wp_politeia_office_terms"] += 1
        
        print(f"  ✓ Processed {len(candidates)} candidates")

if __name__ == "__main__":
    merger = SenatorMerger()
    merger.load_state()
    merger.open_writers()
    try:
        merger.process_directory()
        print("\n✅ Consolidation Complete!")
    finally:
        merger.close_writers()
