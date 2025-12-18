
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
        
        print("\n--- Inspecting Region Tabs Container ---")
        # Try to find the container
        container = await page.query_selector("ul.res-ul-regiones")
        if container:
            print("Found 'ul.res-ul-regiones'")
            html = await container.inner_html()
            print(f"Inner HTML (first 500 chars): {html[:500]}...")
            
            # Inspect children
            children = await container.query_selector_all("*")
            print(f"Found {len(children)} children elements.")
            
            for i, child in enumerate(children):
                tag = await child.evaluate("el => el.tagName")
                text = (await child.text_content()).strip()
                cls = await child.get_attribute("class")
                visible = await child.is_visible()
                
                print(f"[{i}] {tag} Text='{text}' Class='{cls}' Visible={visible}")
        else:
            print("Could NOT find 'ul.res-ul-regiones'. Searching for other likely containers...")
            
            # Search for "RM" text to find where the tabs are
            rm_els = await page.query_selector_all("text=RM")
            for el in rm_els:
                tag = await el.evaluate("el => el.tagName")
                parent = await el.evaluate("el => el.parentElement.tagName")
                print(f"Found 'RM' in {tag} (Parent: {parent})")
                
                # Print parent HTML
                parent_html = await el.evaluate("el => el.parentElement.outerHTML")
                print(f"Parent HTML: {parent_html[:200]}")

if __name__ == "__main__":
    asyncio.run(main())
