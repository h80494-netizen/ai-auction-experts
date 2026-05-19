import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        
        print("Navigating...")
        await page.goto("https://www.onbid.co.kr", wait_until="networkidle")
        
        # Handle alerts
        page.on("dialog", lambda dialog: print(f"Alert: {dialog.message}"))
        
        print("Injecting JS...")
        try:
            await page.evaluate("""
                var inp = document.getElementById('mainSwd');
                if(inp) inp.value = '2026-0400-023211';
                var btn = document.getElementById('mainSwdBtn');
                if(btn) btn.click();
            """)
            print("Clicked via JS")
            await page.wait_for_timeout(5000)
            print("New URL:", page.url)
            await page.screenshot(path="js_search.png")
        except Exception as e:
            print("Error in JS:", e)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
