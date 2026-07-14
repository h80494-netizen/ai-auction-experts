import asyncio
from playwright.async_api import async_playwright
import os
import sys
from dotenv import load_dotenv

load_dotenv('backend/.env')
MYAUCTION_ID = os.getenv('MYAUCTION_ID')
MYAUCTION_PW = os.getenv('MYAUCTION_PW')

async def test():
    print(f"MYAUCTION_ID: {MYAUCTION_ID}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print('Navigating to login...', flush=True)
        await page.goto('https://www.my-auction.co.kr/member/login.php')
        await page.fill('#id', MYAUCTION_ID)
        await page.fill('#passwd', MYAUCTION_PW)
        await page.click('#btn_login')
        
        try:
            await page.wait_for_url('**/main.php', timeout=5000)
            print('Logged in successfully!', flush=True)
        except Exception as e:
            print('Login failed or timeout:', e, flush=True)
        
        print('Searching for case 2025-100759 on MyAuction...', flush=True)
        try:
            # Select year 2025
            await page.select_option("form[name='frm_top2'] select[name='sno']", "2025")
            # Fill case number 100759
            await page.fill("form[name='frm_top2'] input[name='tno']", "100759")
            print('Clicking search...', flush=True)
            await page.click("#tk_btn a")
            await page.wait_for_timeout(2000)
            print('Current URL after search:', page.url, flush=True)
            
            rows = page.locator('table.list-table tbody tr, table tbody tr')
            count = await rows.count()
            print('Rows found:', count, flush=True)
            for i in range(count):
                row_text = await rows.nth(i).inner_text()
                lines = [line.strip() for line in row_text.splitlines() if line.strip()]
                print(f"Row {i} lines:", lines)
        except Exception as e:
            print('Error during search:', e, flush=True)
        
        await browser.close()

asyncio.run(test())
