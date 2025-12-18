"""
GhostMouse Scraper for 2021 Presidential Elections
Uses PyAutoGUI + Playwright to bypass 'isTrusted' checks by performing physical clicks.

REQUIRES:
pip install pyautogui
"""
import asyncio
import random
import math
from playwright.async_api import async_playwright
import pyautogui

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
        Uses window.screenX/Y and estimates UI overhead.
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
        # Usually: Window Height - Viewport Height
        # Note: This includes bottom borders too, but mostly top on Mac
        ui_height = metrics['outerHeight'] - metrics['innerHeight']
        
        # Screen X/Y are usually in "CSS Pixels" on Mac (logical), same as PyAutoGUI usually
        # But we need to be careful with Retina displays. 
        # PyAutoGUI treats coordinates in logical pixels on Mac (usually).
        
        # Origin of viewport
        origin_x = metrics['screenX']
        origin_y = metrics['screenY'] + ui_height 
        
        print(f"Debug - Window: ({metrics['screenX']}, {metrics['screenY']})")
        print(f"Debug - UI Height Estimate: {ui_height}")
        print(f"Debug - Est. Viewport Origin: ({origin_x}, {origin_y})")
        
        return origin_x, origin_y

    async def click_element(self, region_code):
        """Finds element by data-region attribute, calculates screen pos, and clicks"""
        print(f"Looking for region: '{region_code}'")
        
        # Use the specific selector found by the user
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
        
        # Move Mouse (Human-like curve? No, getting data is priority, direct move is fine for now)
        # But let's be slightly gentle
        pyautogui.moveTo(target_x, target_y, duration=0.5)
        
        # Click
        pyautogui.click()
        return True

async def main():
    print("="*60)
    print("GHOST MOUSE SCRAPER - 2021 PRESIDENTIAL")
    print("="*60)
    print("WARNING: I will control your mouse. Do NOT touch it while I run.")
    print("To abort: Slam your mouse to a corner (failsafe) or Ctrl+C")
    print("\n1. Make sure Chrome is open at: https://www.emol.com/especiales/2021/nacional/carrera-presidencial/resultados.asp")
    print("2. Make sure the window is visible on your main screen (not minimized)")
    print("3. Press ENTER to start...")
    input()

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            # Find Emol page (Reuse logic)
            page = None
            for ctx in browser.contexts:
                for p_obj in ctx.pages:
                    if "emol.com" in p_obj.url:
                        page = p_obj
                        await page.bring_to_front()
                        break
                if page: break
            
            if not page:
                print("⚠️ Emol tab not found! Opening it now...")
                if browser.contexts:
                    context = browser.contexts[0]
                else:
                    context = await browser.new_context()
                
                page = await context.new_page()
                await page.goto("https://www.emol.com/especiales/2021/nacional/carrera-presidencial/resultados.asp")
                await page.wait_for_load_state("domcontentloaded")
                print("✅ Page opened successfully.")
            
            ghost = GhostClicker(page)
            
            # Full Region List
            regions = ["XV", "I", "II", "III", "IV", "V", "RM", "VI", "VII", "XVI", "VIII", "IX", "XIV", "X", "XI", "XII"]
            
            import json
            import os

            # Base path for the project root (one level up from GhostMouse)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            for region_code in regions:
                region_communes_data = []
                
                print(f"\n{'='*40}")
                print(f"👻 GhostMouse: Processing Region {region_code}...")
                
                # 1. Click Region to expand menu
                if await ghost.click_element(region_code):
                    print("   Region Clicked. Waiting for menu expansion (3s)...")
                    await asyncio.sleep(3)
                    
                    # 2. Find Communes in the menu
                    region_ul_selector = f"ul[data-region='{region_code.lower()}']"
                    commune_lis = await page.locator(f"{region_ul_selector} li[data-el='p']").all()
                    print(f"   Found {len(commune_lis)} entries in menu.")
                    
                    for i, li in enumerate(commune_lis):
                        try:
                            li_text = (await li.text_content()).strip()
                            
                            if "Total" in li_text or "General" in li_text:
                                continue
                                
                            print(f"\n   👉 Processing Commune: {li_text}")
                            
                            await li.scroll_into_view_if_needed()
                            await asyncio.sleep(0.5)
                            
                            box = await li.bounding_box()
                            if box:
                                vp_x, vp_y = await ghost.get_viewport_offset()
                                target_x = vp_x + box['x'] + (box['width'] / 2)
                                target_y = vp_y + box['y'] + (box['height'] / 2)
                                
                                pyautogui.moveTo(target_x, target_y, duration=0.3)
                                pyautogui.click()
                                
                                print("   Click sent. Waiting for data (3s)...")
                                await asyncio.sleep(3)
                                
                                # 5. Extract Data
                                commune_data = {
                                    "commune": li_text,
                                    #"region_id": region_code, # Removed as per user request
                                    "candidates": [],
                                    "stats": {}
                                }
                                
                                # Candidates
                                candidates = await page.query_selector_all("ul.res-ul-candidatos li")
                                for cand_li in candidates:
                                    name_el = await cand_li.query_selector("div.res-candidato b")
                                    name = (await name_el.text_content()).strip() if name_el else "Unknown"
                                    
                                    party_el = await cand_li.query_selector("div.res-candidato span abbr")
                                    party = (await party_el.get_attribute("title")) if party_el else "Unknown"
                                    if party == "Unknown":
                                         party_el_txt = await cand_li.query_selector("div.res-candidato span")
                                         party = (await party_el_txt.text_content()).strip() if party_el_txt else "Unknown"

                                    votes_el = await cand_li.query_selector("div.res-votos i")
                                    votes_str = (await votes_el.text_content()).strip().replace(".", "") if votes_el else "0"
                                    
                                    pct_el = await cand_li.query_selector("div.res-votos span")
                                    pct_str = (await pct_el.text_content()).strip().replace(",", ".").replace("%", "") if pct_el else "0"
                                    
                                    commune_data["candidates"].append({
                                        "name": name,
                                        "party": party,
                                        "votes": int(votes_str),
                                        "percentage": float(pct_str),
                                        "elected": False 
                                    })
                                
                                # Stats
                                valid_el = await page.query_selector("dl.res-resumen-votacion dt[data-voto='v'] i")
                                valid = int((await valid_el.text_content()).strip().replace(".", "")) if valid_el else 0
                                
                                blank_el = await page.query_selector("dl.res-resumen-votacion dt[data-voto='b'] i")
                                blank = int((await blank_el.text_content()).strip().replace(".", "")) if blank_el else 0
                                
                                null_el = await page.query_selector("dl.res-resumen-votacion dt[data-voto='n'] i")
                                null = int((await null_el.text_content()).strip().replace(".", "")) if null_el else 0
                                
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
                                
                                region_communes_data.append(commune_data)
                                print(f"     Collected: {total_votes} total votes")
                                
                            else:
                                print("     Could not get bounding box for commune")
                                
                        except Exception as e:
                            print(f"     Error scraping commune: {e}")

                else:
                    print(f"   ❌ Failed to click Region {region_code}")
                
                # Save Data for this Region
                if region_communes_data:
                    # Determine path: GhostMouse/scraped_data_2021_presidentes/{REGION}/region_{code}_data.json
                    ghost_mouse_dir = os.path.dirname(os.path.abspath(__file__))
                    target_dir = os.path.join(ghost_mouse_dir, "scraped_data_2021_presidentes", region_code)
                    
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
