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
        
        print("Logging in to MyAuction...")
        await page.goto("https://www.my-auction.co.kr/member/login.php")
        await page.fill("#id", MYAUCTION_ID)
        await page.fill("#passwd", MYAUCTION_PW)
        await page.click("#btn_login")
        await page.wait_for_url("**/main.php", timeout=5000)
        print("Login successful. Current URL:", page.url)
        
        cookies = await context.cookies()
        print(f"Active cookies ({len(cookies)}):")
        for cookie in cookies:
            print(f"  Name: {cookie['name']}, Domain: {cookie['domain']}, Path: {cookie['path']}, Secure: {cookie.get('secure')}, SameSite: {cookie.get('sameSite')}")
            
        # Try navigating directly to pop_detail.php on the SAME page (page, not doc_page)
        idx = "1479806"
        doc_url = f"https://www.my-auction.co.kr/view/pop_detail.php?type=mul&idx={idx}"
        print(f"Navigating SAME page to: {doc_url}")
        await page.goto(doc_url)
        await page.wait_for_timeout(2000)
        html = await page.content()
        print(f"HTML Length: {len(html)}")
        print("Snippet:")
        print(html[:300].strip())
        
        # Try HTTP same page
        doc_url_http = f"http://www.my-auction.co.kr/view/pop_detail.php?type=mul&idx={idx}"
        print(f"Navigating SAME page to HTTP: {doc_url_http}")
        await page.goto(doc_url_http)
        await page.wait_for_timeout(2000)
        html_http = await page.content()
        print(f"HTTP HTML Length: {len(html_http)}")
        print("Snippet:")
        print(html_http[:300].strip())
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
