import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env')
load_dotenv(dotenv_path=env_path)

MYAUCTION_ID = os.getenv("MYAUCTION_ID", "lgs3397")
MYAUCTION_PW = os.getenv("MYAUCTION_PW", "3397lgs")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("Logging in...")
        await page.goto("https://www.my-auction.co.kr/member/login.php")
        await page.fill("#id", MYAUCTION_ID)
        await page.fill("#passwd", MYAUCTION_PW)
        await page.click("#btn_login")
        await page.wait_for_url("**/main.php", timeout=5000)
        
        idx = "1479806"
        detail_url = f"https://www.my-auction.co.kr/view/{idx}"
        print(f"Loading detail page: {detail_url}")
        await page.goto(detail_url)
        await page.wait_for_load_state('networkidle')
        
        # Now try to load pop_detail.php WITH Referer
        doc_url = f"https://www.my-auction.co.kr/view/pop_detail.php?type=mul&idx={idx}"
        print(f"Visiting with Referer: {doc_url}")
        
        doc_page = await context.new_page()
        await doc_page.goto(doc_url, referer=detail_url)
        await doc_page.wait_for_timeout(2000)
        
        html = await doc_page.content()
        print(f"HTML Length: {len(html)}")
        print("HTML snippet (first 300 chars):")
        print(html[:300].strip())
        
        if "매각물건명세서" in html or "임차인" in html or "사건번호" in html:
            print("SUCCESS: Setting Referer loaded the page successfully!")
        else:
            print("FAILURE: Referer did not work.")
            
        await doc_page.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
