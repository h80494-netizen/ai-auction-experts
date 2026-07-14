import asyncio
import os
import sys
from playwright.async_api import async_playwright

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env')
load_dotenv(dotenv_path=env_path)

MYAUCTION_ID = os.getenv("MYAUCTION_ID", "")
MYAUCTION_PW = os.getenv("MYAUCTION_PW", "")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("Logging in...")
            await page.goto("https://www.my-auction.co.kr/member/login.php", wait_until="domcontentloaded")
            await page.fill("#id", MYAUCTION_ID)
            await page.fill("#passwd", MYAUCTION_PW)
            async with page.expect_navigation():
                await page.click("#btn_login")
            
            try:
                await page.wait_for_url("**/main.php", timeout=5000)
            except:
                pass
            await page.wait_for_timeout(2000)
            print("Logged in successfully.")
            
            print("Going to search page...")
            await page.goto('https://www.my-auction.co.kr/auction/search.php', wait_until="domcontentloaded")
            
            print("Selecting Radio button stc=2...")
            await page.locator("form[name='frm'] input[name='stc'][value='2']").check()
            
            print("Filling Sno=2024, Tno=3291...")
            await page.select_option("form[name='frm'] select[name='sno']", "2024")
            await page.locator("form[name='frm'] input[name='tno']").fill("3291")
            
            print("Clearing dates...")
            await page.evaluate("document.getElementsByName('ipdate1')[0].value = ''")
            await page.evaluate("document.getElementsByName('ipdate2')[0].value = ''")
            
            print("Clicking search...")
            async with page.expect_navigation(timeout=15000):
                await page.click("form[name='frm'] button:has-text('검색')")
            
            print(f"Search done. Current URL: {page.url}")
            await page.wait_for_timeout(2000)
            
            # Print rows
            rows = page.locator("table.tbl_auction_list tbody tr, table.tbl_auction_list tr")
            count = await rows.count()
            print(f"Found {count} rows in results table:")
            for i in range(count):
                txt = await rows.nth(i).inner_text()
                print(f"Row {i}: {txt.strip().replace('\n', ' ')[:200]}")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
