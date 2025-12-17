"""
Investigation Script for 2021 Elections
Extracts Region and Commune IDs to compare with 2024
"""
import asyncio
import json
from playwright.async_api import async_playwright

async def investigate_ids():
    print("="*60)
    print("2021 ELECTION ID DISCOVERY")
    print("="*60)
    
    # Instructions
    print("\n📋 INSTRUCTIONS:")
    print("1. Make sure Chrome is running with start_chrome_debug.sh")
    print("2. Navigate to: https://www.emol.com/especiales/2021/nacional/carrera-presidencial/resultados.asp")
    print("3. Click 'PRESIDENCIAL' tab if not selected")
    print("4. Press ENTER here...")
    input()
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            # Find Emol tab
            page = None
            for ctx in browser.contexts:
                for p_obj in ctx.pages:
                    if "emol.com" in p_obj.url:
                        page = p_obj
                        await page.bring_to_front()
                        break
                if page: break
            
            if not page:
                print("❌ Emol tab not found!")
                return

            print(f"✓ Connected to: {page.url}")
            
            # Extract Regions from the top bar
            # Based on user image: <div class="microsite-menu"> or similar with region codes
            print("\nSCANNING REGIONS...")
            
            # Try to find the region buttons/links
            # In 2024 they were in a specific nav. Let's look for common patterns.
            # Strategy: Find Elements that look like region buttons (Roman numerals)
            
            # Just dump all links that might be regions
            regions = await page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a, div, span, li'));
                const roman = /^(XV|I|II|III|IV|V|RM|VI|VII|XVI|VIII|IX|XIV|X|XI|XII)$/;
                
                return links
                    .filter(el => roman.test(el.innerText.trim()))
                    .map(el => ({
                        text: el.innerText.trim(),
                        id: el.getAttribute('id'),
                        class: el.className,
                        href: el.getAttribute('href'),
                        onclick: el.getAttribute('onclick')
                    }));
            }""")
            
            print(f"Found {len(regions)} potential region elements:")
            unique_regions = {}
            for r in regions:
                print(f"  • {r['text']}: ID={r['id']} Class={r['class']}")
                if r['text'] not in unique_regions:
                    unique_regions[r['text']] = r

            print(f"\nUnique Regions Found: {list(unique_regions.keys())}")
            
            # Now let's try to find communes if a region is selected
            # Note: This is an investigation script, so we might need to iterate
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(investigate_ids())
