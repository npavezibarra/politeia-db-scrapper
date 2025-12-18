"""
GhostMouse Scraper for 2021 Diputados Elections
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
import re

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

    async def click_tab(self, tab_name):
        """Clicks a main navigation tab (e.g., DIPUTADOS)"""
        print(f"Looking for tab: '{tab_name}'")
        
        # Selector for the tab - Try targeting the SPAN inside the LI which is the actual tab
        # Based on debug output: [1] Tag: SPAN, Text: 'Diputados', Parent: LI.activo
        selector = "li span:text-is('Diputados'), li span:text-is('DIPUTADOS')"
        
        loc = self.page.locator(selector).first
        if not await loc.count():
            print(f"Could not find tab with selector '{selector}'")
            return False

        box = await loc.bounding_box()
        if not box:
            print("Tab found but invisible!")
            return False
            
        # Calculate center of element in Viewport coordinates
        elem_center_x = box['x'] + (box['width'] / 2)
        elem_center_y = box['y'] + (box['height'] / 2)
        
        # Get Viewport Screen Origin
        vp_x, vp_y = await self.get_viewport_offset()
        
        # Target Screen Coordinates
        target_x = vp_x + elem_center_x
        target_y = vp_y + elem_center_y
        
        print(f"Targeting tab: ({target_x}, {target_y})")
        
        # Move Mouse
        pyautogui.moveTo(target_x, target_y, duration=0.5)
        
        # Click
        pyautogui.click()
        return True

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

    async def click_distrito(self, distrito_selector):
        """Clicks a distrito in the left panel"""
        print(f"Looking for distrito with selector: '{distrito_selector}'")
        
        loc = self.page.locator(distrito_selector).first
        if not await loc.count():
            print(f"Could not find distrito with selector '{distrito_selector}'")
            return False

        box = await loc.bounding_box()
        if not box:
            print("Distrito found but invisible!")
            return False
            
        # Calculate center of element in Viewport coordinates
        elem_center_x = box['x'] + (box['width'] / 2)
        elem_center_y = box['y'] + (box['height'] / 2)
        
        # Get Viewport Screen Origin
        vp_x, vp_y = await self.get_viewport_offset()
        
        # Target Screen Coordinates
        target_x = vp_x + elem_center_x
        target_y = vp_y + elem_center_y
        
        print(f"Targeting distrito: ({target_x}, {target_y})")
        
        # Move Mouse
        pyautogui.moveTo(target_x, target_y, duration=0.5)
        
        # Click
        pyautogui.click()
        return True

async def extract_distrito_data(page, region_code):
    """Extracts all data for the currently displayed distrito"""
    
    # Get distrito header info
    header_el = await page.query_selector("div.res-box-content h3")
    if not header_el:
        print("   ⚠️ Could not find distrito header")
        return None
    
    header_text = (await header_el.text_content()).strip()
    
    # Parse distrito number and name from text
    # Example raw text might be: "Distrito 283Antártica..." or similar issues due to <i> tag
    # Better to extract parts individually
    
    # Distrito Number
    # usually in the text node: "Distrito 28"
    full_text = await header_el.evaluate("el => el.childNodes[0].nodeValue")
    distrito_match = re.search(r'Distrito\s+(\d+)', full_text)
    distrito_id = int(distrito_match.group(1)) if distrito_match else 0
    
    # Escaños (Seats) - Found in the <i> tag inside h3
    escanos_el = await header_el.query_selector("i")
    escanos_totales = int((await escanos_el.text_content()).strip()) if escanos_el else 0
    
    # Communes - Found in the <span> tag inside h3
    communes_el = await header_el.query_selector("span")
    communes_text = (await communes_el.text_content()).strip() if communes_el else ""
    
    # Parse communes string into a list
    # "Comuna1, Comuna2, Comuna3 y Comuna4."
    raw_comunas = communes_text.replace(".", "").replace(" y ", ", ")
    comunas_list = [c.strip() for c in raw_comunas.split(",") if c.strip()]
    
    distrito_data = {
        "region": "",  # To be filled by caller or inferred
        "distrito_id": distrito_id,
        "comunas": comunas_list,
        "escaños_totales": escanos_totales,
        "pactos": [],
        "resumen_votacion": {}
    }
    
    # Extract pacts and candidates
    # Logic: Iterate through children of ul.res-ul-candidatos
    # h5 -> Start of new Pact
    # li -> Candidate belonging to current Pact
    
    ul_candidates = await page.query_selector("ul.res-ul-candidatos")
    if not ul_candidates:
        print("   ⚠️ Could not find candidate list")
        return distrito_data
        
    # Get all direct children (h5 and li)
    children = await ul_candidates.query_selector_all("> *")
    
    current_pact = None
    
    for child in children:
        tag_name = await child.evaluate("el => el.tagName")
        
        if tag_name == "H5":
            pact_text = (await child.text_content()).strip()
            # "AA. Chile Podemos +" -> "AA. Chile Podemos +"
            
            current_pact = {
                "pacto_nombre": pact_text,
                "candidatos": []
            }
            distrito_data["pactos"].append(current_pact)
            
        elif tag_name == "LI" and current_pact is not None:
            # Extract candidate info
            cand_li = child
            
            # Name
            name_el = await cand_li.query_selector("div.res-candidato b")
            name = (await name_el.text_content()).strip() if name_el else "Unknown"
            
            # Party info from abbr title
            party_el = await cand_li.query_selector("div.res-candidato span abbr")
            title_attr = (await party_el.get_attribute("title")) if party_el else ""
            
            # Determine Condición (Militante vs Independiente)
            # Logic: If title contains "Independiente", condition is "Independiente"
            # Else "Militante"
            is_independent = "Independiente" in title_attr
            condicion = "Independiente" if is_independent else "Militante"
            
            # Party Name
            # If independent quota: "Independiente en cupo Evópoli" -> Party is "Evópoli" (simplified) or full string?
            # User example: "UDI" (Militante), "UDI" (Independiente)
            # From debug: "Independiente ( PRI )"
            
            # Let's try to extract the specific party name.
            # If "Independiente en cupo X", party is X.
            # If "Partid X", party is X.
            
            # Try getting the text content of the party line (which might contain abbreviation)
            # Debug: "Independiente ( PRI )"
            party_text_content = (await party_el.text_content()).strip() if party_el else ""
            
            # Fallback party name from data-sub
            party_abbr = (await cand_li.get_attribute("data-sub")) or ""
            
            party_final = party_abbr # Default to abbreviation as requested in example ("UDI")
            
            # Votes
            votes_el = await cand_li.query_selector("div.res-votos i")
            votes_str = (await votes_el.text_content()).strip().replace(".", "") if votes_el else "0"
            
            # Percentage
            pct_el = await cand_li.query_selector("div.res-votos span")
            pct_str = (await pct_el.text_content()).strip().replace(",", ".").replace("%", "") if pct_el else "0"
            
            # Elected
            class_attr = await cand_li.get_attribute("class")
            is_elected = "ganador" in class_attr if class_attr else False
            
            candidate_obj = {
                "nombre": name,
                "partido": party_final,
                "condicion": condicion,
                "porcentaje_votos": float(pct_str) if pct_str.replace(".", "").isdigit() else 0.0,
                "votos_totales": int(votes_str) if votes_str.isdigit() else 0,
                "electo": is_elected
            }
            
            current_pact["candidatos"].append(candidate_obj)
            
    # Extract summary statistics
    valid_el = await page.query_selector("dl.res-resumen-votacion dt[data-voto='v'] i")
    valid = int((await valid_el.text_content()).strip().replace(".", "")) if valid_el else 0
    
    blank_el = await page.query_selector("dl.res-resumen-votacion dt[data-voto='b'] i")
    blank = int((await blank_el.text_content()).strip().replace(".", "")) if blank_el else 0
    
    null_el = await page.query_selector("dl.res-resumen-votacion dt[data-voto='n'] i")
    null = int((await null_el.text_content()).strip().replace(".", "")) if null_el else 0
    
    total_sufragios = valid + blank + null
    
    distrito_data["resumen_votacion"] = {
        "votos_validos": valid,
        "votos_blancos": blank,
        "votos_nulos": null,
        "total_sufragios": total_sufragios
    }
    
    return distrito_data

async def main():
    print("="*60)
    print("GHOST MOUSE SCRAPER - 2021 DIPUTADOS")
    print("="*60)
    print("WARNING: I will control your mouse. Do NOT touch it while I run.")
    print("To abort: Slam your mouse to a corner (failsafe) or Ctrl+C")
    print("\n1. Make sure Chrome is open with remote debugging")
    print("   Run: ./start_chrome_debug.sh")
    print("2. Navigate to: https://www.emol.com/especiales/2021/nacional/carrera-presidencial/resultados.asp")
    print("3. Make sure the window is visible on your main screen (not minimized)")
    print("4. Press ENTER to start...")
    input()

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            print(f"✅ Connected to browser. Contexts: {len(browser.contexts)}")
            
            # Find Emol page
            page = None
            if not browser.contexts:
                 print("   ⚠️ No browser contexts found!")
            
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
                return
            
            ghost = GhostClicker(page)
            
            # Step 1: Click DIPUTADOS tab
            print("\n" + "="*60)
            print("STEP 1: Clicking DIPUTADOS tab...")
            print("="*60)
            
            if await ghost.click_tab("DIPUTADOS"):
                print("✅ DIPUTADOS tab clicked. Waiting for page to load (5s)...")
                await asyncio.sleep(5)
                
                # Re-acquire page reference after navigation
                print("   Re-acquiring page reference after navigation...")
                page = None
                for ctx in browser.contexts:
                    for p_obj in ctx.pages:
                        url = p_obj.url
                        if "emol.com" in url and "resultados.asp" in url:
                            page = p_obj
                            await page.bring_to_front()
                            print(f"   ✅ Found page: {url}")
                            break
                    if page: break
                
                if not page:
                    print("   ❌ Could not find Emol page after clicking tab!")
                    return
                
                # Update ghost clicker with new page reference
                ghost = GhostClicker(page)
            else:
                print("❌ Failed to click DIPUTADOS tab. Aborting.")
                return
            
            # All regions to process
            target_regions = ["XV", "I", "II", "III", "IV", "V", "RM", "VI", "VII", "XVI", "VIII", "IX", "XIV", "X", "XI", "XII", "EXT"]
            
            # Base path for output
            ghost_mouse_dir = os.path.dirname(os.path.abspath(__file__))
            
            for region_code in target_regions:
                print(f"\n{'='*60}")
                print(f"👻 Processing Region: {region_code}")
                print(f"{'='*60}")
                
            for region_code in target_regions:
                print(f"\n{'='*60}")
                print(f"👻 Processing Region: {region_code}")
                print(f"{'='*60}")
                
                # Click region using the robust data-region attribute selector found in debug
                # HTML: <li title="..." data-region="xv">XV</li>
                region_selector = f"li[data-region='{region_code.lower()}']"
                
                print(f"   Looking for region '{region_code}' with selector '{region_selector}'")
                
                region_found = False
                
                # Try the data-attribute selector
                loc = page.locator(region_selector).first
                if await loc.count() > 0:
                     if await ghost.click_element(region_code): 
                         region_found = True
                
                if not region_found:
                    # Fallback to pure text match if data attribute fails
                    print(f"   Using text fallback for Region {region_code}")
                    text_loc = page.locator(f"li:text-is('{region_code}')").first
                    if await text_loc.count():
                        box = await text_loc.bounding_box()
                        if box:
                            cx = box['x'] + box['width']/2
                            cy = box['y'] + box['height']/2
                            vp_x, vp_y = await ghost.get_viewport_offset()
                            pyautogui.moveTo(vp_x + cx, vp_y + cy, duration=0.5)
                            pyautogui.click()
                            region_found = True
                
                if not region_found:
                    print(f"   ❌ Failed to click Region {region_code}. Skipping...")
                    continue
                
                print("   ✅ Region clicked. Waiting for distritos to load (4s)...")
                await asyncio.sleep(4)
                
                # Get region name
                region_name_el = await page.query_selector("div#res-box-info h3")
                region_name = (await region_name_el.text_content()).strip() if region_name_el else f"Region {region_code}"
                
                # Find all distritos in the left panel
                # Selector: ul[data-region='xv'] li:has-text('Distrito')
                distrito_links = await page.query_selector_all(f"ul[data-region='{region_code.lower()}'] li:has-text('Distrito')")
                
                # Fallback: just visible distritos
                if not distrito_links:
                     distrito_links = await page.query_selector_all("li:has-text('Distrito'):visible")
                
                print(f"   Found {len(distrito_links)} distrito(s) in region {region_code}")
                
                region_data = {
                    "region_code": region_code,
                    "region_name": region_name,
                    "distritos": []
                }
                
                # Process each distrito
                for idx, distrito_link in enumerate(distrito_links):
                    distrito_text = (await distrito_link.text_content()).strip()
                    # Clean up text to just "Distrito X" for logging
                    short_name = distrito_text.split('.')[0] if '.' in distrito_text else distrito_text[:20]
                    print(f"\n   📍 Distrito {idx+1}/{len(distrito_links)}: {short_name}...")
                    
                    # Click distrito
                    # We need the element's position to click it
                    box = await distrito_link.bounding_box()
                    if box:
                        # Use ghost click manually
                        cx = box['x'] + box['width']/2
                        cy = box['y'] + box['height']/2
                        vp_x, vp_y = await ghost.get_viewport_offset()
                        
                        print(f"      Targeting: ({vp_x + cx}, {vp_y + cy})")
                        pyautogui.moveTo(vp_x + cx, vp_y + cy, duration=0.5)
                        pyautogui.click()
                        
                        print(f"      ✅ Clicked. Waiting for data (4s)...")
                        await asyncio.sleep(4)
                        
                        # Extract data
                        distrito_data = await extract_distrito_data(page, region_code)
                        
                        if distrito_data:
                            region_data["distritos"].append(distrito_data)
                            print(f"      ✅ Extracted {len(distrito_data.get('pacts', []))} pacts")
                        else:
                            print(f"      ⚠️ Failed to extract data")
                    else:
                        print(f"      ❌ Distrito invisible or no number")
                
                # Save region data
                if region_data["distritos"]:
                    target_dir = os.path.join(ghost_mouse_dir, "scrap_data_2021_diputados", region_code)
                    
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    
                    filename = f"region_{region_code.lower()}_diputados.json"
                    output_path = os.path.join(target_dir, filename)
                    
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(region_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"\n✅ Saved Region {region_code} data to {output_path}")
                    print(f"   Total distritos: {len(region_data['distritos'])}")
                else:
                    print(f"\n⚠️ No data collected for Region {region_code}")
                
                await asyncio.sleep(1)

            print(f"\n{'='*60}")
            print("✅ ALL REGIONS PROCESSED!")
            print(f"{'='*60}")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
