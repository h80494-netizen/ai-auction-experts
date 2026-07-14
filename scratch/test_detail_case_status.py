import asyncio
from playwright.async_api import async_playwright
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv('backend/.env')
MYAUCTION_ID = os.getenv('MYAUCTION_ID')
MYAUCTION_PW = os.getenv('MYAUCTION_PW')

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Handle dialogs
        async def handle_dialog(dialog):
            print(f"Dialog: {dialog.message}")
            await dialog.dismiss()
        page.on("dialog", lambda dialog: asyncio.create_task(handle_dialog(dialog)))
        
        # Login
        await page.goto('http://www.my-auction.co.kr/member/login.php')
        await page.fill('#id', MYAUCTION_ID)
        await page.fill('#passwd', MYAUCTION_PW)
        await page.click('#btn_login')
        await page.wait_for_url('**/main.php')
        
        # Search
        await page.select_option("form[name='frm_top2'] select[name='sno']", "2025")
        await page.fill("form[name='frm_top2'] input[name='tno']", "100759")
        await page.click("#tk_btn a")
        await page.wait_for_url("**/search_list.php*")
        
        # Find row and link
        rows = page.locator('table.tbl_auction_list tbody tr, table.tbl_auction_list tr')
        count = await rows.count()
        detail_url = None
        for i in range(count):
            row_text = await rows.nth(i).inner_text()
            if "100759" in row_text:
                print(f"Row {i} text: {row_text.splitlines()}")
                link = rows.nth(i).locator("a[href*='/view/']").first
                if await link.count() > 0:
                    href = await link.get_attribute("href")
                    detail_url = href if href.startswith("http") else f"https://www.my-auction.co.kr{href}"
                    break
        
        if detail_url:
            print(f"Going to detail page: {detail_url}")
            await page.goto(detail_url)
            await page.wait_for_load_state('networkidle')
            
            # Print page title
            print(f"Detail Page Title: {await page.title()}")
            
            # Print all TH and TD contents
            from bs4 import BeautifulSoup
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            print("\n--- TH & TD Values ---")
            for th in soup.find_all('th'):
                td = th.find_next_sibling('td')
                if td:
                    print(f"{th.get_text(strip=True)} : {td.get_text(strip=True)}")
                    
            # Print history (기일내역)
            print("\n--- History (hisdiv) ---")
            hisdiv = soup.find('div', id='hisdiv')
            if hisdiv:
                for tr in hisdiv.find_all('tr'):
                    print([td.get_text(strip=True) for td in tr.find_all('td')])
            else:
                print("No hisdiv found")
                
            # Write page html to a file to examine
            with open("scratch/case_detail_dump.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("\nDumped HTML to scratch/case_detail_dump.html")
        else:
            print("No detail url found!")
            
        await browser.close()

asyncio.run(test())
