import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

load_dotenv()
MYAUCTION_ID = os.getenv('MYAUCTION_ID')
MYAUCTION_PW = os.getenv('MYAUCTION_PW')

async def test():
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
            print('On main.php!', flush=True)
        except Exception as e:
            print('Error waiting for main.php:', e, flush=True)
        
        print('Filling frm_top2...', flush=True)
        try:
            await page.select_option("form[name='frm_top2'] select[name='sno']", "2024")
            await page.fill("form[name='frm_top2'] input[name='tno']", "5020")
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
                address = ""
                for line in lines:
                    if "시" in line or "도" in line or "동" in line:
                        if len(line) > 10 and not address:
                            address = line
                if address:
                    link_href = "No link"
                    links = rows.nth(i).locator("a")
                    link_count = await links.count()
                    for j in range(link_count):
                        href = await links.nth(j).get_attribute("href")
                        if href and ("/view/" in href or "view" in href):
                            link_href = href
                            break
                    print(f'Row {i} address: {address.encode("cp949", errors="ignore").decode("cp949")} | Link: {link_href}')
        except Exception as e:
            print('Error during search:', e, flush=True)
        
        await browser.close()

asyncio.run(test())
