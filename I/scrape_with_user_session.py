"""
Session Hijacking Scraper for Region I
Uses the user's authenticated browser session to bypass bot detection
"""
import asyncio
import csv
import os
from datetime import datetime
from playwright.async_api import async_playwright

OUTPUT_DIR = "/Users/nicolas/Desktop/PoliteiaDB/I"

# Region I communes
TARAPACA_COMMUNES = [
    ("Alto Hospicio", "2502"),
    ("Camiña", "2504"),
    ("Colchane", "2505"),
    ("Huara", "2506"),
    ("Iquique", "2501"),
    ("Pica", "2507"),
    ("Pozo Almonte", "2503")
]

async def extract_commune_data(page, commune_name):
    """Extract data from the currently loaded commune page"""
    print(f"\n{'='*60}")
    print(f"Extracting data for: {commune_name}")
    print(f"{'='*60}")
    
    data = {
        'commune': commune_name,
        'candidates': [],
        'stats': {}
    }
    
    # Wait for candidate list to be visible
    try:
        await page.wait_for_selector("ul.res-ul-candidatos", state="visible", timeout=5000)
        print("✓ Candidate list found")
    except:
        print("✗ Candidate list not visible")
        return None
    
    # Extract candidates
    candidates = await page.query_selector_all("ul.res-ul-candidatos li")
    print(f"Found {len(candidates)} candidates:")
    
    for li in candidates:
        try:
            # Name
            name_el = await li.query_selector("div.res-candidato > b")
            name = (await name_el.text_content()).strip() if name_el else "Unknown"
            
            # Party
            party_el = await li.query_selector("div.res-candidato > span")
            party = (await party_el.text_content()).strip() if party_el else "Unknown"
            
            # Votes
            votes_el = await li.query_selector("div.res-votos i")
            votes_str = (await votes_el.text_content()).strip().replace(".", "") if votes_el else "0"
            votes = int(votes_str) if votes_str.isdigit() else 0
            
            # Percentage
            pct_el = await li.query_selector("div.res-votos span")
            pct_str = (await pct_el.text_content()).strip().replace(",", ".").replace("%", "") if pct_el else "0"
            pct = float(pct_str) if pct_str else 0.0
            
            # Elected?
            class_attr = await li.get_attribute("class")
            elected = "ganador" in (class_attr or "")
            
            candidate = {
                'name': name,
                'party': party,
                'votes': votes,
                'percentage': pct,
                'elected': elected
            }
            
            data['candidates'].append(candidate)
            
            status = "🏆 ELECTED" if elected else ""
            print(f"  • {name:30} {votes:>6} votes ({pct:>5}%) {status}")
            
        except Exception as e:
            print(f"  Error extracting candidate: {e}")
    
    # Extract statistics
    try:
        # Valid votes
        v_el = await page.query_selector('dl.res-resumen-votacion dt[data-voto="v"] i')
        valid = (await v_el.text_content()).strip().replace(".", "") if v_el else "0"
        
        # Blank votes
        b_el = await page.query_selector('dl.res-resumen-votacion dt[data-voto="b"] i')
        blank = (await b_el.text_content()).strip().replace(".", "") if b_el else "0"
        
        # Null votes
        n_el = await page.query_selector('dl.res-resumen-votacion dt[data-voto="n"] i')
        null = (await n_el.text_content()).strip().replace(".", "") if n_el else "0"
        
        # Total votes
        vot_el = await page.query_selector('ol.res-participacion li[data-year="2024"] span[data-part="vot"]')
        total = (await vot_el.text_content()).strip().replace(".", "") if vot_el else "0"
        
        # Participation rate
        pcj_el = await page.query_selector('ol.res-participacion li[data-year="2024"] b[data-part="pcj"]')
        part_rate = (await pcj_el.text_content()).strip().replace(",", ".") if pcj_el else "0"
        
        data['stats'] = {
            'valid_votes': int(valid) if valid.isdigit() else 0,
            'blank_votes': int(blank) if blank.isdigit() else 0,
            'null_votes': int(null) if null.isdigit() else 0,
            'total_votes': int(total) if total.isdigit() else 0,
            'participation_rate': float(part_rate) if part_rate else 0.0
        }
        
        print(f"\nStatistics:")
        print(f"  Valid: {data['stats']['valid_votes']:,}")
        print(f"  Blank: {data['stats']['blank_votes']:,}")
        print(f"  Null: {data['stats']['null_votes']:,}")
        print(f"  Total: {data['stats']['total_votes']:,}")
        print(f"  Participation: {data['stats']['participation_rate']}%")
        
    except Exception as e:
        print(f"Error extracting statistics: {e}")
    
    return data

async def session_hijack_scraper():
    """
    Connect to user's existing Chrome browser and scrape data
    """
    print("="*60)
    print("SESSION HIJACKING SCRAPER")
    print("="*60)
    print("\nThis scraper will:")
    print("1. Connect to YOUR Chrome browser (you must start it specially)")
    print("2. Wait for you to navigate and authenticate")
    print("3. Extract data from each commune as you click through")
    print("\n" + "="*60)
    
    # Instructions for user
    print("\n📋 INSTRUCTIONS:")
    print("\n1. Close ALL Chrome windows")
    print("\n2. Open Terminal and run:")
    print("   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\")
    print("   --remote-debugging-port=9222 \\")
    print("   --user-data-dir=/tmp/chrome-debug")
    print("\n3. In the Chrome window that opens:")
    print("   - Go to: https://www.emol.com/especiales/2024/nacional/elecciones2024/resultados.asp")
    print("   - Click 'Alcaldes'")
    print("   - Click Region 'I' (Tarapacá)")
    print("   - Browse around a bit (scroll, move mouse)")
    print("\n4. Come back here and press ENTER when ready...")
    
    input()
    
    print("\n🔌 Connecting to your Chrome browser...")
    
    async with async_playwright() as p:
        try:
            # Connect to existing Chrome instance
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            contexts = browser.contexts
            
            if not contexts:
                print("❌ No browser contexts found. Did you start Chrome with --remote-debugging-port=9222?")
                return
            
            # Use the first context (your browsing session)
            context = contexts[0]
            pages = context.pages
            
            if not pages:
                print("❌ No pages found. Please open the Emol website in Chrome first.")
                return
            
            # Use the active page
            page = pages[0]
            
            print(f"✓ Connected to page: {page.url}")
            
            # Collect data for all communes
            all_data = []
            
            for commune_name, emol_id in TARAPACA_COMMUNES:
                print(f"\n\n{'='*60}")
                print(f"Ready to scrape: {commune_name}")
                print(f"{'='*60}")
                print(f"\n👉 Please click on '{commune_name}' in the sidebar")
                print("   Wait for the data to load (3-5 seconds)")
                print("   Then press ENTER here...")
                
                input()
                
                # Extract data from current page
                data = await extract_commune_data(page, commune_name)
                
                if data:
                    all_data.append(data)
                    print(f"\n✓ Successfully extracted data for {commune_name}")
                else:
                    print(f"\n✗ Failed to extract data for {commune_name}")
                
                # Small delay
                await asyncio.sleep(1)
            
            # Save to JSON for inspection
            import json
            output_file = os.path.join(OUTPUT_DIR, "region_i_data.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n\n{'='*60}")
            print(f"✓ COMPLETE! Data saved to: {output_file}")
            print(f"{'='*60}")
            print(f"\nExtracted data for {len(all_data)}/{len(TARAPACA_COMMUNES)} communes")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nMake sure you:")
            print("1. Started Chrome with --remote-debugging-port=9222")
            print("2. Opened the Emol website in that Chrome window")
            print("3. Are browsing as a human (not redirected)")

if __name__ == "__main__":
    asyncio.run(session_hijack_scraper())
