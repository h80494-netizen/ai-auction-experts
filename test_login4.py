import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv('backend/.env')
MYAUCTION_ID = os.environ.get('MYAUCTION_ID')
MYAUCTION_PW = os.environ.get('MYAUCTION_PW')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        async def handle_dialog(dialog):
            print(f"Alert: {dialog.message}")
            await dialog.dismiss()
        page.on("dialog", handle_dialog)
        
        print(f"Login as {MYAUCTION_ID}")
        await page.goto("http://www.my-auction.co.kr/member/login.php")
        await page.fill("#id", MYAUCTION_ID)
        await page.fill("#passwd", MYAUCTION_PW)
        await page.click("#btn_login")
        await page.wait_for_url("**/main.php", timeout=8000)
        
        year = '2024'
        num = '5020'
        
        print(f"Going to search.php")
        await page.goto("http://www.my-auction.co.kr/auction/search.php")
        
        # Click search button
        await page.evaluate(f"document.frm.sno.value = '{year}'; document.frm.tno.value = '{num}'; document.frm.submit();")
        
        await page.wait_for_load_state('domcontentloaded')
        await page.wait_for_timeout(2000)
        
        print(f"URL after search: {page.url}")
        
        rows = page.locator("table.tbl_auction_list tbody tr, table.tbl_auction_list tr")
        count = await rows.count()
        print(f"Rows count: {count}")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
