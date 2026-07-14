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
            print("Accessing login page...")
            await page.goto("https://www.my-auction.co.kr/member/login.php", wait_until="domcontentloaded")
            await page.fill("#id", MYAUCTION_ID)
            await page.fill("#passwd", MYAUCTION_PW)
            async with page.expect_navigation():
                await page.click("#btn_login")
            print("Login button clicked. Waiting for main.php redirect...")
            try:
                await page.wait_for_url("**/main.php", timeout=5000)
            except:
                pass
            await page.wait_for_timeout(2000)
            print("Logged in.")
            
            print("Going to search page...")
            await page.goto('https://www.my-auction.co.kr/auction/search.php', wait_until="domcontentloaded")
            await page.select_option("form[name='frm'] select[name='sno']", "2024")
            await page.locator("form[name='frm'] input[name='tno']").fill("6060")
            await page.evaluate("document.getElementsByName('ipdate1')[0].value = ''")
            await page.evaluate("document.getElementsByName('ipdate2')[0].value = ''")
            
            print("Clicking search...")
            async with page.expect_navigation():
                await page.click("form[name='frm'] button:has-text('검색')")
            
            print(f"Results page loaded. URL: {page.url}")
            await page.wait_for_timeout(2000)
            
            # Save screenshot of default "Active" page
            await page.screenshot(path="scratch/tab_active.png")
            print("Saved active tab screenshot to scratch/tab_active.png")
            
            # Find and click "Scheduled" or "Completed" tabs
            # Let's search for links that contain pchs=Y or schs=Y on the page
            print("Searching for status tab links...")
            links = page.locator("a")
            count = await links.count()
            
            scheduled_link = None
            completed_link = None
            
            for i in range(count):
                href = await links.nth(i).get_attribute("href")
                if href:
                    if "schs=Y" in href:
                        scheduled_link = links.nth(i)
                        print(f"Found Scheduled tab link: {href}")
                    elif "pchs=Y" in href:
                        completed_link = links.nth(i)
                        print(f"Found Completed/Sold tab link: {href}")
            
            if scheduled_link:
                print("Clicking Scheduled tab...")
                # Scheduled tab click might navigate or refresh
                async with page.expect_navigation(timeout=10000):
                    await scheduled_link.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path="scratch/tab_scheduled.png")
                rows = page.locator("table.tbl_auction_list tbody tr, table.tbl_auction_list tr")
                rcount = await rows.count()
                print(f"Scheduled tab: Found {rcount} table rows.")
                if rcount > 1:
                    print("Scheduled row text:", await rows.nth(1).inner_text())
                
                # Go back to results to click Completed tab
                await page.go_back()
                await page.wait_for_timeout(2000)
            
            # Re-fetch completed link since page went back
            completed_link = None
            links = page.locator("a")
            count = await links.count()
            for i in range(count):
                href = await links.nth(i).get_attribute("href")
                if href and "pchs=Y" in href:
                    completed_link = links.nth(i)
            
            if completed_link:
                print("Clicking Completed/Sold tab...")
                async with page.expect_navigation(timeout=10000):
                    await completed_link.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path="scratch/tab_completed.png")
                rows = page.locator("table.tbl_auction_list tbody tr, table.tbl_auction_list tr")
                rcount = await rows.count()
                print(f"Completed tab: Found {rcount} table rows.")
                if rcount > 1:
                    print("Completed row text:", await rows.nth(1).inner_text())
            else:
                print("Completed tab link not found on the page.")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
