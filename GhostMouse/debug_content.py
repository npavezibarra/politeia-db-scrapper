
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        
        # Find Emol page
        page = None
        for ctx in browser.contexts:
            for p_obj in ctx.pages:
                if "emol.com" in p_obj.url:
                    page = p_obj
                    break
            if page: break
        
        if not page:
            print("Emol page not found")
            return

        print(f"Current URL: {page.url}")
        
        # Assuming a district is ALREADY selected/loaded on the screen from the previous run
        print("\n--- Inspecting Content Box ---")
        
        content_box = await page.query_selector("div.res-box-content")
        if content_box:
            # Print HTML snippet
            html = await content_box.inner_html()
            print(f"Content Box HTML (first 1000 chars): {html[:1000]}...")
            
            # Check for candidate lists
            uls = await content_box.query_selector_all("ul")
            print(f"Found {len(uls)} <ul> elements in content box.")
            
            for i, ul in enumerate(uls):
                cls = await ul.get_attribute("class")
                print(f"UL [{i}] Class: {cls}")
                
            # Check for Headers (Pact names)
            h5s = await content_box.query_selector_all("h5")
            print(f"Found {len(h5s)} <h5> elements (Pacts?)")
            for h5 in h5s:
                text = (await h5.text_content()).strip()
                print(f"  H5: {text}")

            # Check for Escaños (Seats) info
            # User mentioned "escaños_totales": 8. Need to find "8" or "8 escaños"
            escanos_el = await page.query_selector("text=/escaños/i") 
            if escanos_el:
                 txt = await escanos_el.text_content()
                 print(f"Found text with 'escaños': {txt}")
        else:
            print("Could NOT find 'div.res-box-content'")

if __name__ == "__main__":
    asyncio.run(main())
