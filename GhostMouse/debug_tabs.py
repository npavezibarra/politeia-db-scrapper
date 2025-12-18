
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
        
        # Inspect all elements with text DIPUTADOS
        print(f"Searching for any element with text 'DIPUTADOS'...")
        
        elements = await page.query_selector_all("text=DIPUTADOS")
        print(f"Found {len(elements)} elements with text 'DIPUTADOS'.")
        
        for i, el in enumerate(elements):
            tag = await el.evaluate("el => el.tagName")
            text = (await el.text_content()).strip()
            cls = await el.get_attribute("class")
            
            print(f"[{i}] Tag: {tag}, Text: '{text}', Class: '{cls}'")
            
            # Get parent info too
            parent_tag = await el.evaluate("el => el.parentElement.tagName")
            parent_cls = await el.evaluate("el => el.parentElement.className")
            print(f"    Parent: {parent_tag}.{parent_cls}")
            
            box = await el.bounding_box()
            if box:
                print(f"    Visible at: {box}")
            else:
                print(f"    Hidden")

if __name__ == "__main__":
    asyncio.run(main())
