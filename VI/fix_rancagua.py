"""
Fix Rancagua data - re-scrape just this commune
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

async def fix_rancagua():
    print("Connecting to your Chrome browser...")
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0]
        
        print(f"Connected to: {page.url}")
        print("\n👉 Click on 'Rancagua' in the sidebar")
        print("   Wait for data to load (5 seconds)")
        print("   Then press ENTER...")
        
        input()
        
        print("\nExtracting Rancagua data...")
        
        # Wait for candidate list
        await page.wait_for_selector("ul.res-ul-candidatos", state="visible", timeout=5000)
        
        candidates = []
        candidate_lis = await page.query_selector_all("ul.res-ul-candidatos li")
        
        for li in candidate_lis:
            name_el = await li.query_selector("div.res-candidato > b")
            name = (await name_el.text_content()).strip() if name_el else "Unknown"
            
            party_el = await li.query_selector("div.res-candidato > span")
            party = (await party_el.text_content()).strip() if party_el else "Unknown"
            
            votes_el = await li.query_selector("div.res-votos i")
            votes_str = (await votes_el.text_content()).strip().replace(".", "") if votes_el else "0"
            votes = int(votes_str) if votes_str.isdigit() else 0
            
            pct_el = await li.query_selector("div.res-votos span")
            pct_str = (await pct_el.text_content()).strip().replace(",", ".").replace("%", "") if pct_el else "0"
            pct = float(pct_str) if pct_str else 0.0
            
            class_attr = await li.get_attribute("class")
            elected = "ganador" in (class_attr or "")
            
            candidates.append({
                'name': name,
                'party': party,
                'votes': votes,
                'percentage': pct,
                'elected': elected
            })
            
            status = "🏆 ELECTED" if elected else ""
            print(f"  • {name:30} {votes:>6} votes ({pct:>5}%) {status}")
        
        # Extract stats
        v_el = await page.query_selector('dl.res-resumen-votacion dt[data-voto="v"] i')
        valid = int((await v_el.text_content()).strip().replace(".", "")) if v_el else 0
        
        b_el = await page.query_selector('dl.res-resumen-votacion dt[data-voto="b"] i')
        blank = int((await b_el.text_content()).strip().replace(".", "")) if b_el else 0
        
        n_el = await page.query_selector('dl.res-resumen-votacion dt[data-voto="n"] i')
        null = int((await n_el.text_content()).strip().replace(".", "")) if n_el else 0
        
        vot_el = await page.query_selector('ol.res-participacion li[data-year="2024"] span[data-part="vot"]')
        total = int((await vot_el.text_content()).strip().replace(".", "")) if vot_el else 0
        
        pcj_el = await page.query_selector('ol.res-participacion li[data-year="2024"] b[data-part="pcj"]')
        part_rate = float((await pcj_el.text_content()).strip().replace(",", ".")) if pcj_el else 0.0
        
        stats = {
            'valid_votes': valid,
            'blank_votes': blank,
            'null_votes': null,
            'total_votes': total,
            'participation_rate': part_rate
        }
        
        print(f"\nStatistics:")
        print(f"  Valid: {valid:,}")
        print(f"  Blank: {blank:,}")
        print(f"  Null: {null:,}")
        print(f"  Total: {total:,}")
        print(f"  Participation: {part_rate}%")
        
        # Load existing data
        json_path = '/Users/nicolas/Desktop/PoliteiaDB/VI/region_vi_data.json'
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
        except:
            data = []
        
        # Update or add Rancagua
        found = False
        for commune in data:
            if commune['commune'] == 'Rancagua':
                commune['candidates'] = candidates
                commune['stats'] = stats
                found = True
                break
        
        if not found:
            # Insert at beginning or append? Let's just append if not found, usually user starts with Rancagua so maybe insert at 0
            data.insert(0, {
                'commune': 'Rancagua',
                'candidates': candidates,
                'stats': stats
            })
        
        # Save
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("\n✓ Rancagua data updated!")

if __name__ == "__main__":
    asyncio.run(fix_rancagua())
