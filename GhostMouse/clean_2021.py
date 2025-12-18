
import csv
import os
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

ELECTION_DATE = "2021-11-21"
TERM_START_DATE = "2022-03-11"

def clean_csvs():
    print("🧹 Cleaning 2021 Election Data...")
    
    # 1. Identify Election IDs to remove
    election_ids_to_remove = set()
    
    elections_path = os.path.join(DATA_DIR, "wp_politeia_elections.csv")
    temp_elections = os.path.join(DATA_DIR, "wp_politeia_elections.tmp")
    
    if os.path.exists(elections_path):
        with open(elections_path, 'r', encoding='utf-8') as f_in, \
             open(temp_elections, 'w', encoding='utf-8', newline='') as f_out:
            
            reader = csv.DictReader(f_in)
            writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
            writer.writeheader()
            
            for row in reader:
                if row['election_date'] == ELECTION_DATE:
                    election_ids_to_remove.add(row['id'])
                else:
                    writer.writerow(row)
        
        shutil.move(temp_elections, elections_path)
        print(f"  - Removed {len(election_ids_to_remove)} elections from wp_politeia_elections.csv")
    
    if not election_ids_to_remove:
        print("  - No 2021 elections found to clean.")
        return

    # 2. Clean wp_politeia_election_results
    clean_by_election_id("wp_politeia_election_results", election_ids_to_remove)
    
    # 3. Clean wp_politeia_candidacies
    clean_by_election_id("wp_politeia_candidacies", election_ids_to_remove)
    
    # 4. Clean wp_politeia_party_memberships (by date)
    clean_by_date("wp_politeia_party_memberships", "started_on", ELECTION_DATE)
    
    # 5. Clean wp_politeia_office_terms (by date)
    clean_by_date("wp_politeia_office_terms", "started_on", TERM_START_DATE)

    print("✅ Cleanup Complete.")

def clean_by_election_id(table_name, election_ids):
    file_path = os.path.join(DATA_DIR, f"{table_name}.csv")
    temp_path = os.path.join(DATA_DIR, f"{table_name}.tmp")
    
    if os.path.exists(file_path):
        removed_count = 0
        with open(file_path, 'r', encoding='utf-8') as f_in, \
             open(temp_path, 'w', encoding='utf-8', newline='') as f_out:
            
            reader = csv.DictReader(f_in)
            writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
            writer.writeheader()
            
            for row in reader:
                if row['election_id'] in election_ids:
                    removed_count += 1
                else:
                    writer.writerow(row)
        
        shutil.move(temp_path, file_path)
        print(f"  - Removed {removed_count} rows from {table_name}.csv")

def clean_by_date(table_name, date_col, target_date):
    file_path = os.path.join(DATA_DIR, f"{table_name}.csv")
    temp_path = os.path.join(DATA_DIR, f"{table_name}.tmp")
    
    if os.path.exists(file_path):
        removed_count = 0
        with open(file_path, 'r', encoding='utf-8') as f_in, \
             open(temp_path, 'w', encoding='utf-8', newline='') as f_out:
            
            reader = csv.DictReader(f_in)
            writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
            writer.writeheader()
            
            for row in reader:
                if row[date_col] == target_date:
                    removed_count += 1
                else:
                    writer.writerow(row)
        
        shutil.move(temp_path, file_path)
        print(f"  - Removed {removed_count} rows from {table_name}.csv")

if __name__ == "__main__":
    clean_csvs()
