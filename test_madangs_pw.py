import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://madangs.com/popup/detail_report?link=photo&code=0320240058264001&type=1&photo_idx=2", wait_until="networkidle")
        html = await page.content()
        with open("madangs_dump.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        # Check if images exist
        img_locators = page.locator("img")
        count = await img_locators.count()
        print(f"Total images found by playwright: {count}")
        for i in range(count):
            src = await img_locators.nth(i).get_attribute("src")
            alt = await img_locators.nth(i).get_attribute("alt")
            print(f"IMG {i}: {src} | alt: {alt}")
            
        await browser.close()

asyncio.run(main())
