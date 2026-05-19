import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")
MYAUCTION_ID = os.getenv("MYAUCTION_ID")
MYAUCTION_PW = os.getenv("MYAUCTION_PW")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Login...")
        await page.goto("https://www.my-auction.co.kr/member/login.php")
        await page.fill("#id", MYAUCTION_ID)
        await page.fill("#passwd", MYAUCTION_PW)
        await page.click("#btn_login")
        await page.wait_for_timeout(2000)
        
        print("Searching...")
        await page.goto("https://www.my-auction.co.kr/auction/search.php")
        await page.select_option("select[name='sno']", "2024")
        await page.locator("input[name='tno']").first.fill("5020")
        await page.click("button:has-text('검색')")
        await page.wait_for_load_state("networkidle")
        
        print("Clicking result...")
        result_link = page.locator("a[href*='/view/'], .result-list a, .list-table a, td.num a").first
        if await result_link.count() > 0:
            await result_link.click()
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)
            html2 = await page.content()
            with open("detail_result.html", "w", encoding="utf-8") as f:
                f.write(html2)
            print("Done writing detail_result.html")
        else:
            print("No result found!")
            html = await page.content()
            with open("search_result.html", "w", encoding="utf-8") as f:
                f.write(html)
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
