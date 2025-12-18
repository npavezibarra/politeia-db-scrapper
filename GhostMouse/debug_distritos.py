
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
        
        # 1. Inspect the Region Selector (just to verify)
        print("\n--- Inspecting Region Buttons ---")
        regions = await page.query_selector_all("ul.res-ul-regiones li")
        print(f"Found {len(regions)} region buttons.")
        
        # 2. Inspect the Left Sidebar (where Distritos should be)
        print("\n--- Inspecting Left Sidebar (Distritos) ---")
        # Search for any element containing "Distrito"
        distrito_els = await page.query_selector_all("text=/Distrito \d+/")
        print(f"Found {len(distrito_els)} elements with text 'Distrito X'")
        
        for i, el in enumerate(distrito_els):
            text = (await el.text_content()).strip()
            tag = await el.evaluate("el => el.tagName")
            parent_cls = await el.evaluate("el => el.parentElement.className")
            parent_tag = await el.evaluate("el => el.parentElement.tagName")
            
            print(f"[{i}] {tag} '{text}' -> Parent: {parent_tag}.{parent_cls}")
            
            # Print outer HTML of the parent to understand structure
            html = await el.evaluate("el => el.parentElement.outerHTML")
            print(f"    HTML: {html[:200]}...") # First 200 chars

if __name__ == "__main__":
    asyncio.run(main())
