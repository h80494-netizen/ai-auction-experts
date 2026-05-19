import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Login
        await page.goto("https://www.my-auction.co.kr/login.php")
        await page.fill("#id", "lgs3397")
        await page.fill("#passwd", "3397lgs")
        await page.click("#btn_login")
        await page.wait_for_url("**/main.php")
        
        # Open Document (e.g., 매각물건명세서 mul, or 등기부 aceeaea1)
        # We need a valid idx. Let's use 85408 which is a random recent idx.
        idx = '85408'
        print("IDX:", idx)
        
        doc_url = f"https://www.my-auction.co.kr/view/pop_detail.php?type=mul&idx={idx}"
        await page.goto(doc_url)
        await page.wait_for_timeout(3000)
        
        os.makedirs("downloads/test", exist_ok=True)
        await page.pdf(path="downloads/test/mul.pdf", print_background=True)
        print("Saved mul.pdf")
        
        doc_url = f"https://www.my-auction.co.kr/view/pop_detail.php?type=status&idx={idx}"
        await page.goto(doc_url)
        await page.wait_for_timeout(3000)
        await page.pdf(path="downloads/test/status.pdf", print_background=True)
        print("Saved status.pdf")
        
        await browser.close()

asyncio.run(main())
