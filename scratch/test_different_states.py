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
            print("Logged in successfully.")
            
            # We will test three URLs:
            # 1. Active (spels=Y, schs=N, pchs=N)
            # 2. Scheduled (spels=N, schs=Y, pchs=N)
            # 3. Completed/Sold (spels=N, schs=N, pchs=Y)
            states = [
                ("Active (spels=Y)", "https://www.my-auction.co.kr/auction/search_list.php?sno=2024&tno=6060&spels=Y&schs=N&pchs=N&ipdate1=&ipdate2="),
                ("Scheduled (schs=Y)", "https://www.my-auction.co.kr/auction/search_list.php?sno=2024&tno=6060&spels=N&schs=Y&pchs=N&ipdate1=&ipdate2="),
                ("Completed/Sold (pchs=Y)", "https://www.my-auction.co.kr/auction/search_list.php?sno=2024&tno=6060&spels=N&schs=N&pchs=Y&ipdate1=&ipdate2="),
            ]
            
            for name, url in states:
                print(f"\n--- Testing {name} ---")
                await page.goto(url, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)
                
                rows = page.locator("table.tbl_auction_list tbody tr, table.tbl_auction_list tr")
                count = await rows.count()
                print(f"Found {count} rows in table.")
                for i in range(count):
                    txt = await rows.nth(i).inner_text()
                    print(f"Row {i}: {txt.strip().replace('\n', ' ')[:150]}")
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
