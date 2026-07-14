import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to URL...")
        await page.goto("https://www.gg.go.kr/onnuri/view.do?nowUrl=%2Fonnuri%2Fview.do%3Fno%3D109&no=109&sv=A&sc=%EC%9D%98%EC%99%95&sw=%EC%9D%B8%EB%8D%95%EC%9B%90")
        await page.wait_for_timeout(5000)
        
        # Take a screenshot to see what's on the page
        await page.screenshot(path="../../scratch/gg_screenshot.png")
        
        # Check all tables
        tables = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('table')).map(table => {
                return Array.from(table.querySelectorAll('tr')).map(tr => {
                    return Array.from(tr.querySelectorAll('td, th')).map(td => td.innerText.trim());
                });
            });
        }''')
        
        print(f"Found {len(tables)} tables")
        for i, table in enumerate(tables):
            print(f"Table {i}:")
            for row in table[:10]:
                print(row)
        
        # Check list items
        list_items = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('.list li, .board-list li, .item')).map(li => li.innerText.trim().replace(/\\n/g, ' '));
        }''')
        print(f"Found {len(list_items)} list items")
        for li in list_items[:10]:
            print(li)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
