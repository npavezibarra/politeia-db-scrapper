"""
GhostMouse Scraper for 2021 Senatorial Elections
Uses PyAutoGUI + Playwright to bypass 'isTrusted' checks by performing physical clicks.

REQUIRES:
pip install pyautogui playwright
"""
import asyncio
import random
import math
from playwright.async_api import async_playwright
import pyautogui
import json
import os

# Calibration constants for macOS Chrome (Approximate)
# You might need to adjust these if the clicks missed!
TOOLBAR_HEIGHT_ESTIMATE = 80 

class GhostClicker:
    """Handles physical mouse movements and clicks"""
    
    def __init__(self, page):
        self.page = page
        
    async def get_viewport_offset(self):
        """
        Calculates the screen coordinates of the top-left corner of the viewport.
        """
        # Get window position and sizes
        metrics = await self.page.evaluate("""() => {
            return {
                screenX: window.screenX,
                screenY: window.screenY,
                outerWidth: window.outerWidth,
                outerHeight: window.outerHeight,
                innerWidth: window.innerWidth,
                innerHeight: window.innerHeight,
                devicePixelRatio: window.devicePixelRatio
            }
        }""")
        
        # Approximate the top UI height (Tabs + URL bar)
        ui_height = metrics['outerHeight'] - metrics['innerHeight']
        
        # Origin of viewport
        origin_x = metrics['screenX']
        origin_y = metrics['screenY'] + ui_height 
        
        return origin_x, origin_y

    async def click_element(self, region_code):
        """Finds element by data-region attribute, calculates screen pos, and clicks"""
        print(f"Looking for region: '{region_code}'")
        
        # Selector for the Region list item
        selector = f"li[data-region='{region_code.lower()}']"
        
        loc = self.page.locator(selector).first
        if not await loc.count():
            print(f"Could not find element with selector '{selector}'")
            return False

        box = await loc.bounding_box()
        if not box:
            print("Element found but invisible!")
            return False
            
        # Calculate center of element in Viewport coordinates
        elem_center_x = box['x'] + (box['width'] / 2)
        elem_center_y = box['y'] + (box['height'] / 2)
        
        # Get Viewport Screen Origin
        vp_x, vp_y = await self.get_viewport_offset()
        
        # Target Screen Coordinates
        target_x = vp_x + elem_center_x
        target_y = vp_y + elem_center_y
        
        print(f"Targeting: ({target_x}, {target_y})")
        
        # Move Mouse
        pyautogui.moveTo(target_x, target_y, duration=0.5)
        
        # Click
        pyautogui.click()
        return True

async def main():
    print("="*60)
    print("GHOST MOUSE SCRAPER - 2021 SENATORIAL (SENADORES)")
    print("="*60)
    print("WARNING: I will control your mouse. Do NOT touch it while I run.")
    print("To abort: Slam your mouse to a corner (failsafe) or Ctrl+C")
    print("\n1. Make sure Chrome is open and you are on the 'Senadores' tab on Emol.")
    print("   URL: https://www.emol.com/especiales/2021/nacional/carrera-presidencial/resultados.asp")
    print("2. Make sure the window is visible on your main screen (not minimized)")
    print("3. Press ENTER to start...")
    input()

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            print(f"   Connected to browser. Contexts: {len(browser.contexts)}")
            
            # Find Emol page
            page = None
            if not browser.contexts:
                 print("   ⚠️ No browser contexts found! This usually means the Chrome window was closed or didn't launch correctly.")
            
            for ctx in browser.contexts:
                print(f"   Context has {len(ctx.pages)} pages.")
                for p_obj in ctx.pages:
                    url = p_obj.url
                    print(f"   - Found tab: {url}")
                    if "emol.com" in url:
                        page = p_obj
                        await page.bring_to_front()
                        break
                if page: break
            
            if not page:
                print("\n⚠️ Emol tab not found in the debug session!")
                print("   Please ensure you are using the Chrome window launched by 'start_chrome_debug.sh'.")
                print("   If you have another Chrome open, it might be interfering.")
                return
            
            ghost = GhostClicker(page)
            
            # Requested Regions for Senators
            target_regions = ["II", "IV", "RM", "VI", "XVI", "VIII", "XIV", "X", "XII"]
            
            # Base path for the project root
            ghost_mouse_dir = os.path.dirname(os.path.abspath(__file__))
            
            for region_code in target_regions:
                region_communes_data = []
                
                print(f"\n{'='*40}")
                print(f"👻 GhostMouse: Processing Region {region_code}...")
                
                # 1. Click Region to select it
                if await ghost.click_element(region_code):
                    print("   Region Clicked. Waiting for data (3s)...")
                    await asyncio.sleep(4) # Check if longer wait helps
                    
                    # For Senators, we scrape the Regional Total displayed.
                    # Communes might not be selectable or relevant in this view.
                    
                    print(f"\n   👉 Processing Region: {region_code}")
                    
                    # 5. Extract Data (Treating the whole region as one "commune" entry for the JSON structure)
                    # Use a generic name or the region name
                    
                    # Try to get the Region Name from the header if possible, or use code
                    header_el = await page.query_selector("div#res-box-info h3")
                    region_name = (await header_el.text_content()).strip() if header_el else f"Region {region_code}"
                    
                    commune_data = {
                        "commune": region_name, # Storing Region Name here
                        "candidates": [],
                        "stats": {}
                    }
                    
                    # Candidates Extraction
                    candidates_loc = await page.query_selector_all("ul.res-ul-candidatos li")
                    print(f"   Found {len(candidates_loc)} candidates.")
                    
                    for cand_li in candidates_loc:
                        # Name
                        name_el = await cand_li.query_selector("div.res-candidato b")
                        name = (await name_el.text_content()).strip() if name_el else "Unknown"
                        
                        # Party
                        party_el = await cand_li.query_selector("div.res-candidato span abbr")
                        party = (await party_el.get_attribute("title")) if party_el else "Unknown"
                        if party == "Unknown":
                                party_el_txt = await cand_li.query_selector("div.res-candidato span")
                                party = (await party_el_txt.text_content()).strip() if party_el_txt else "Unknown"

                        # Votes
                        votes_el = await cand_li.query_selector("div.res-votos i")
                        votes_str = (await votes_el.text_content()).strip().replace(".", "") if votes_el else "0"
                        
                        # Percentage
                        pct_el = await cand_li.query_selector("div.res-votos span")
                        pct_str = (await pct_el.text_content()).strip().replace(",", ".").replace("%", "") if pct_el else "0"
                        
                        # Elected Status
                        class_attr = await cand_li.get_attribute("class")
                        is_elected = "ganador" in class_attr if class_attr else False
                        
                        commune_data["candidates"].append({
                            "name": name,
                            "party": party,
                            "votes": int(votes_str),
                            "percentage": float(pct_str),
                            "elected": is_elected
                        })
                    
                    # Stats Extraction
                    valid_el = await page.query_selector("dl.res-resumen-votacion dt[data-voto='v'] i")
                    valid = int((await valid_el.text_content()).strip().replace(".", "")) if valid_el else 0
                    
                    blank_el = await page.query_selector("dl.res-resumen-votacion dt[data-voto='b'] i")
                    blank = int((await blank_el.text_content()).strip().replace(".", "")) if blank_el else 0
                    
                    null_el = await page.query_selector("dl.res-resumen-votacion dt[data-voto='n'] i")
                    null = int((await null_el.text_content()).strip().replace(".", "")) if null_el else 0
                    
                    # Participation Rate
                    padron_el = await page.query_selector("ol.res-resumen-zona li[data-stat='p'] span.reset")
                    padron_text = (await padron_el.text_content()).strip().replace(".", "") if padron_el else "0"
                    padron = int(padron_text.split()[0]) 
                    
                    total_votes = valid + blank + null
                    
                    part_rate = 0.0
                    if padron > 0:
                        part_rate = round((total_votes / padron) * 100, 2)
                        
                    commune_data["stats"] = {
                        "valid_votes": valid,
                        "blank_votes": blank,
                        "null_votes": null,
                        "total_votes": total_votes,
                        "participation_rate": part_rate
                    }
                    
                    # Add to the list
                    region_communes_data.append(commune_data)
                    
                    print(json.dumps(commune_data, indent=2, ensure_ascii=False))

                else:
                    print(f"   ❌ Failed to click Region {region_code}")
                
                # Save Data for this Region
                if region_communes_data:
                    # Path: GhostMouse/scraped_data_2021_senators/{REGION}/region_{code}_data.json
                    target_dir = os.path.join(ghost_mouse_dir, "scraped_data_2021_senators", region_code)
                    
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    
                    filename = f"region_{region_code.lower()}_data.json"
                    output_path = os.path.join(target_dir, filename)
                    
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(region_communes_data, f, indent=2, ensure_ascii=False)
                    print(f"✅ Saved Region {region_code} data to {output_path}")
                
                await asyncio.sleep(1)

            print(f"\n✅ All regions processed.")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
