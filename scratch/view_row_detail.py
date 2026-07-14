import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
MYAUCTION_ID = os.getenv('MYAUCTION_ID')
MYAUCTION_PW = os.getenv('MYAUCTION_PW')

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto('https://www.my-auction.co.kr/member/login.php')
        await page.fill('#id', MYAUCTION_ID)
        await page.fill('#passwd', MYAUCTION_PW)
        await page.click('#btn_login')
        await page.wait_for_url('**/main.php')
        
        # Go to search list directly
        await page.goto('http://www.my-auction.co.kr/auction/search_list.php?aresult=all&sno=2025&tno=100759')
        await page.wait_for_timeout(2000)
        
        rows = page.locator('table.list-table tbody tr, table tbody tr')
        count = await rows.count()
        print(f"Total rows: {count}")
        for i in range(count):
            row_html = await rows.nth(i).inner_html()
            row_text = await rows.nth(i).inner_text()
            if "100759" in row_text:
                print(f"Row {i} contains 100759.")
                print(f"HTML of Row {i}:")
                print(row_html)
                print("---------------------------------")
        
        await browser.close()

asyncio.run(test())
