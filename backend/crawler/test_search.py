import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Go to search...")
        await page.goto("https://www.my-auction.co.kr/auction/search.php")
        print("Fill 2024, 5020")
        await page.select_option("select[name='sno']", "2024")
        await page.locator("input[name='tno']").first.fill("5020")
        await page.click("button:has-text('검색')")
        print("Wait for load...")
        await page.wait_for_load_state("networkidle")
        
        # Get all rows
        rows = page.locator("table tbody tr")
        count = await rows.count()
        print(f"Total results: {count}")
        for i in range(count):
            text = await rows.nth(i).inner_text()
            print(f"Row {i}: {text.replace(chr(10), ' ')}")
            
        await browser.close()

asyncio.run(main())
