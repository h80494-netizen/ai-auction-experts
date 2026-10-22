import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://www.my-auction.co.kr/main/main.php")
        html = await page.content()
        with open("main_dump.html", "w", encoding="utf-8") as f:
            f.write(html)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
