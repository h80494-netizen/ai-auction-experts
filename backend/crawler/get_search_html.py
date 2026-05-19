import asyncio, os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()
MYAUCTION_ID = os.getenv('MYAUCTION_ID')
MYAUCTION_PW = os.getenv('MYAUCTION_PW')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://www.my-auction.co.kr/member/login.php')
        await page.fill('#id', MYAUCTION_ID)
        await page.fill('#passwd', MYAUCTION_PW)
        await page.click('#btn_login')
        await page.wait_for_timeout(2000)
        
        await page.goto('https://www.my-auction.co.kr/auction/search.php')
        await page.select_option("select[name='sno']", "2024")
        await page.locator("input[name='tno']").first.fill("5020")
        await page.click("button:has-text('검색')")
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)
        
        html = await page.content()
        with open("search_table.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Done")
        await browser.close()

asyncio.run(main())
