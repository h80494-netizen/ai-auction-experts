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
    print(f"ID: {MYAUCTION_ID}, PW: {'*' * len(MYAUCTION_PW)}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("Accessing login page...")
            await page.goto("https://www.my-auction.co.kr/member/login.php", wait_until="domcontentloaded", timeout=15000)
            
            print("Filling login form...")
            await page.wait_for_selector("#id", state="visible", timeout=5000)
            await page.fill("#id", MYAUCTION_ID)
            await page.fill("#passwd", MYAUCTION_PW)
            
            print("Clicking login button...")
            async with page.expect_navigation(timeout=10000):
                await page.click("#btn_login")
            
            print(f"Logged in. Current URL: {page.url}")
            
            print("Going to search page...")
            await page.goto('https://www.my-auction.co.kr/auction/search.php', wait_until="domcontentloaded", timeout=15000)
            
            print("Filling search fields: Sno=2024, Tno=6060...")
            await page.select_option("form[name='frm'] select[name='sno']", "2024")
            await page.locator("form[name='frm'] input[name='tno']").fill("6060")
            
            print("Clearing date fields ipdate1 and ipdate2 via evaluate...")
            await page.evaluate("document.getElementsByName('ipdate1')[0].value = ''")
            await page.evaluate("document.getElementsByName('ipdate2')[0].value = ''")
            
            print("Clicking search button...")
            async with page.expect_navigation(timeout=15000):
                await page.click("form[name='frm'] button:has-text('검색')")
            
            print(f"Search done. Current URL: {page.url}")
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            with open("scratch/search_result_6060.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Saved search result HTML to scratch/search_result_6060.html")
            
            await page.screenshot(path="scratch/search_result_6060.png")
            print("Saved screenshot to scratch/search_result_6060.png")
            
            # Count rows
            rows = page.locator("table.tbl_auction_list tbody tr, table.tbl_auction_list tr")
            count = await rows.count()
            print(f"Number of rows found in tbl_auction_list: {count}")
            for i in range(count):
                txt = await rows.nth(i).inner_text()
                print(f"Row {i}: {txt[:100]}...")
                
        except Exception as e:
            print(f"Error occurred: {e}")
            try:
                html = await page.content()
                with open("scratch/search_error_6060.html", "w", encoding="utf-8") as f:
                    f.write(html)
                await page.screenshot(path="scratch/search_error_6060.png")
            except:
                pass
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
