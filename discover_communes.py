"""
Discover Communes Script (Debug Mode)
Prints all available regions to help identify the correct one
"""
import asyncio
from playwright.async_api import async_playwright

async def discover_all_regions():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.pages[0]
            
            print(f"Connected to: {page.url}")
            
            # Find all regions
            regions = await page.query_selector_all("ul.res-ul-regiones > li")
            print(f"Found {len(regions)} regions:")
            
            for i, region in enumerate(regions):
                text = await region.text_content()
                data_region = await region.get_attribute("data-region")
                print(f"[{i}] Text: '{text.strip()}' | data-region: '{data_region}'")
                
                # Check if this is Valparaiso
                if data_region == "v" or "Valparaíso" in text:
                    print("   -> CANDIDATE FOR REGION V! Clicking...")
                    try:
                        await region.click()
                        await asyncio.sleep(2)
                        
                        # Try to get communes
                        communes = await page.query_selector_all(f"li[data-region='{data_region}'] ul.res-ul-comunas li")
                        if not communes and data_region:
                             # Try alternate selector if data-region based one fails
                             # Maybe the ul is inside the li?
                             communes = await region.query_selector_all("ul.res-ul-comunas li")
                        
                        print(f"   -> Found {len(communes)} communes:")
                        for c in communes:
                            c_name = await c.text_content()
                            c_id = await c.get_attribute("data-id")
                            print(f"      (\"{c_name.strip()}\", \"{c_id}\"),")
                    except Exception as e:
                        print(f"   -> Error interacting: {e}")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(discover_all_regions())
