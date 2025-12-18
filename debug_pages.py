
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            print(f"Connected to browser. Contexts: {len(browser.contexts)}")
            
            found_any = False
            for i, ctx in enumerate(browser.contexts):
                print(f"Context {i}: {len(ctx.pages)} pages")
                for page in ctx.pages:
                    print(f" - URL: {page.url}")
                    found_any = True
                    
            if not found_any:
                print("No pages found in any context!")
                
        except Exception as e:
            print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
