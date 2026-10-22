import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://madangs.com/goview?g_code=20250800059271")
        await page.wait_for_timeout(3000)
        html = await page.content()
        with open("madangs_test.html", "w", encoding="utf-8") as f:
            f.write(html)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
