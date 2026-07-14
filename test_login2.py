import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import urllib.parse

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
        
        params = {
            "usage_code_all": "", "stitle": "", "spe_age": "", "gm_age": "",
            "npls": "N", "spels": "Y", "schs": "N", "pchs": "N",
            "address2_01": "", "address2_02": "", "address2_03": "", "acharge_01": "",
            "ps_alert": "", "stc": "1", "address1_01": "", "address1_02": "", "address1_03": "",
            "ipdate1": "2026-06-09", "ipdate2": "2026-09-07", "eprice1": "0", "eprice2": "0",
            "sno": year, "tno": num, "regal": "", "mprice1": "0", "mprice2": "0",
            "barea1": "", "barea2": "", "np1": "", "np2": "", "apoint1": "0", "apoint2": "0",
            "larea1": "", "larea2": "", "buildingtxt": "", "aresult": "", "aorder": "1"
        }
        
        query_string = urllib.parse.urlencode(params)
        search_url = f"http://www.my-auction.co.kr/auction/search_list.php?{query_string}"
        
        print(f"Navigating to {search_url}")
        await page.goto(search_url)
        await page.wait_for_load_state('domcontentloaded')
        await page.wait_for_timeout(2000)
        
        rows = page.locator("table.tbl_auction_list tbody tr, table.tbl_auction_list tr")
        count = await rows.count()
        print(f"Rows count: {count}")
        if count > 0:
            text = await rows.nth(min(1, count - 1)).inner_text()
            print(f"Row: {text[:100]}")
        else:
            print("No rows found!")
            html = await page.content()
            with open("search_fail.html", "w", encoding="utf-8") as f:
                f.write(html)
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
