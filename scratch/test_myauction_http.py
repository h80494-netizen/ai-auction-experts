import asyncio
import os
import re
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
        
        print("Logging in to MyAuction...")
        await page.goto("https://www.my-auction.co.kr/member/login.php")
        await page.fill("#id", MYAUCTION_ID)
        await page.fill("#passwd", MYAUCTION_PW)
        await page.click("#btn_login")
        await page.wait_for_url("**/main.php", timeout=5000)
        
        # We know the idx is 1479806
        idx = "1479806"
        
        # Test HTTP
        doc_url = f"http://www.my-auction.co.kr/view/pop_detail.php?type=mul&idx={idx}"
        print(f"Visiting HTTP URL: {doc_url}")
        
        doc_page = await context.new_page()
        await doc_page.goto(doc_url, wait_until="domcontentloaded")
        await doc_page.wait_for_timeout(2000)
        
        doc_html = await doc_page.content()
        print(f"HTML Length: {len(doc_html)}")
        print("HTML snippet (first 300 chars):")
        print(doc_html[:300].strip())
        
        # Let's see if there is actual table text
        if "매각물건명세서" in doc_html or "임차인" in doc_html or "사건번호" in doc_html:
            print("SUCCESS: Real document page loaded successfully!")
        else:
            print("FAILURE: Still redirected or empty page.")
            
        await doc_page.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
