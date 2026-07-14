import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to gg.go.kr...")
        await page.goto("https://www.gg.go.kr/onnuri/view.do?no=109")
        
        # Wait for the page to load
        await page.wait_for_timeout(3000)
        
        # Look for search button or list elements
        # Usually there's a search button with text '검색' or '조회'
        try:
            await page.click("text=검색", timeout=3000)
            print("Clicked 검색 button")
            await page.wait_for_timeout(3000)
        except Exception as e:
            print("No '검색' button found, trying to find tables...")
            
        # Get all table text to see what data is there
        tables = await page.locator("table").all()
        print(f"Found {len(tables)} tables")
        if tables:
            text = await tables[0].inner_text()
            print("Table 0 preview:")
            print(text[:500])
        else:
            print("No tables found. Dumping DOM to scratch...")
            content = await page.content()
            with open("scratch/gg_dom.html", "w", encoding="utf-8") as f:
                f.write(content)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
