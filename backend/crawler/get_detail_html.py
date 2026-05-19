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
        
        await page.goto('https://www.my-auction.co.kr/view/1394984')
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)
        
        html = await page.content()
        with open("detail_table.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Done")
        await browser.close()

asyncio.run(main())
