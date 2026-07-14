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
            
            # We will test three URLs with stc=2:
            # 1. Active (spels=Y, schs=N, pchs=N, stc=2)
            # 2. Scheduled (spels=N, schs=Y, pchs=N, stc=2)
            # 3. Completed/Sold (spels=N, schs=N, pchs=Y, stc=2)
            states = [
                ("spels", "https://www.my-auction.co.kr/auction/search_list.php?sno=2024&tno=6060&spels=Y&schs=N&pchs=N&ipdate1=&ipdate2=&stc=2"),
                ("schs", "https://www.my-auction.co.kr/auction/search_list.php?sno=2024&tno=6060&spels=N&schs=Y&pchs=N&ipdate1=&ipdate2=&stc=2"),
                ("pchs", "https://www.my-auction.co.kr/auction/search_list.php?sno=2024&tno=6060&spels=N&schs=N&pchs=Y&ipdate1=&ipdate2=&stc=2"),
            ]
            
            for name, url in states:
                print(f"\n--- Testing {name} ---")
                await page.goto(url, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                
                cur_url = page.url
                cur_title = await page.title()
                print(f"Current URL: {cur_url}")
                print(f"Current Title: {cur_title}")
                
                html = await page.content()
                with open(f"scratch/result_{name}.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"Saved html to scratch/result_{name}.html")
                
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
