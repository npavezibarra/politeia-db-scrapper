"""
Merge Region Data Script
Consolidates JSON data from regions into the master CSV files in PoliteiaDB/data
"""
import json
import csv
import os
from datetime import datetime

DATA_DIR = "/Users/nicolas/Desktop/PoliteiaDB/data"

# CSV Tables and Columns
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

OFFICE_ALCALDE = 1
ELECTION_DATE = "2024-10-27"
TERM_START_DATE = "2024-12-06"

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
        print("Loading current state from master CSVs...")
        
        # 1. Load Max IDs and Caches
        for table in TABLES:
            file_path = os.path.join(DATA_DIR, f"{table}.csv")
            max_id = 0
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Update Max ID
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
            f = open(os.path.join(DATA_DIR, f"{table}.csv"), "a", newline="", encoding="utf-8")
            w = csv.DictWriter(f, fieldnames=cols)
            self.files[table] = f
            self.writers[table] = w

    def close(self):
        for f in self.files.values():
            f.close()

    def merge_region(self, json_file, region_name):
        print(f"\nMerging {json_file}...")
        
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
                "office_id": OFFICE_ALCALDE,
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
                        "office_id": OFFICE_ALCALDE,
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
    
    # Merge Region I
    if os.path.exists("/Users/nicolas/Desktop/PoliteiaDB/I/region_i_data.json"):
        merger.merge_region("/Users/nicolas/Desktop/PoliteiaDB/I/region_i_data.json", "Región de Tarapacá")
        
    # Merge Region II
    if os.path.exists("/Users/nicolas/Desktop/PoliteiaDB/II/region_ii_data.json"):
        merger.merge_region("/Users/nicolas/Desktop/PoliteiaDB/II/region_ii_data.json", "Región de Antofagasta")
    # Merge Region III
    if os.path.exists("/Users/nicolas/Desktop/PoliteiaDB/III/region_iii_data.json"):
        merger.merge_region("/Users/nicolas/Desktop/PoliteiaDB/III/region_iii_data.json", "Región de Atacama")
    # Merge Region IV
    if os.path.exists("/Users/nicolas/Desktop/PoliteiaDB/IV/region_iv_data.json"):
        merger.merge_region("/Users/nicolas/Desktop/PoliteiaDB/IV/region_iv_data.json", "Región de Coquimbo")
    # Merge Region V
    if os.path.exists("/Users/nicolas/Desktop/PoliteiaDB/V/region_v_data.json"):
        merger.merge_region("/Users/nicolas/Desktop/PoliteiaDB/V/region_v_data.json", "Región de Valparaíso")
    # Merge Region VI
    if os.path.exists("/Users/nicolas/Desktop/PoliteiaDB/VI/region_vi_data.json"):
        merger.merge_region("/Users/nicolas/Desktop/PoliteiaDB/VI/region_vi_data.json", "Región del Libertador General Bernardo O'Higgins")
    # Merge Region VII
    if os.path.exists("/Users/nicolas/Desktop/PoliteiaDB/VII/region_vii_data.json"):
        merger.merge_region("/Users/nicolas/Desktop/PoliteiaDB/VII/region_vii_data.json", "Región del Maule")
    # Merge Region VIII
    if os.path.exists("/Users/nicolas/Desktop/PoliteiaDB/VIII/region_viii_data.json"):
        merger.merge_region("/Users/nicolas/Desktop/PoliteiaDB/VIII/region_viii_data.json", "Región del Biobío")
    # Merge Region IX
    if os.path.exists("/Users/nicolas/Desktop/PoliteiaDB/IX/region_ix_data.json"):
        merger.merge_region("/Users/nicolas/Desktop/PoliteiaDB/IX/region_ix_data.json", "Región de la Araucanía")
    # Merge Region X
    if os.path.exists("/Users/nicolas/Desktop/PoliteiaDB/X/region_x_data.json"):
        merger.merge_region("/Users/nicolas/Desktop/PoliteiaDB/X/region_x_data.json", "Región de Los Lagos")
    # Merge Region XI
    if os.path.exists("/Users/nicolas/Desktop/PoliteiaDB/XI/region_xi_data.json"):
        merger.merge_region("/Users/nicolas/Desktop/PoliteiaDB/XI/region_xi_data.json", "Región de Aysén del General Carlos Ibáñez del Campo")
    # Merge Region XII
    if os.path.exists("/Users/nicolas/Desktop/PoliteiaDB/XII/region_xii_data.json"):
        merger.merge_region("/Users/nicolas/Desktop/PoliteiaDB/XII/region_xii_data.json", "Región de Magallanes y de la Antártica Chilena")
    # Merge Region XIV
    if os.path.exists("/Users/nicolas/Desktop/PoliteiaDB/XIV/region_xiv_data.json"):
        merger.merge_region("/Users/nicolas/Desktop/PoliteiaDB/XIV/region_xiv_data.json", "Región de Los Ríos")
    # Merge Region XVI
    if os.path.exists("/Users/nicolas/Desktop/PoliteiaDB/XVI/region_xvi_data.json"):
        merger.merge_region("/Users/nicolas/Desktop/PoliteiaDB/XVI/region_xvi_data.json", "Región de Ñuble")
    # Merge Region XV
    if os.path.exists("/Users/nicolas/Desktop/PoliteiaDB/XV/region_xv_data.json"):
        merger.merge_region("/Users/nicolas/Desktop/PoliteiaDB/XV/region_xv_data.json", "Región de Arica y Parinacota")
        
    merger.close()
    print("\n✓ All regions merged into master CSVs!")
