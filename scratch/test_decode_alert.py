import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env')
load_dotenv(dotenv_path=env_path)

MYAUCTION_ID = os.getenv("MYAUCTION_ID")
MYAUCTION_PW = os.getenv("MYAUCTION_PW")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # We will catch alert dialogs and print them!
        page.on("dialog", lambda dialog: print(f"DIALOG ALERT TEXT: {dialog.message}"))
        
        print(f"Logging in as {MYAUCTION_ID}...")
        await page.goto("https://www.my-auction.co.kr/member/login.php")
        await page.fill("#id", MYAUCTION_ID)
        await page.fill("#passwd", MYAUCTION_PW)
        await page.click("#btn_login")
        await page.wait_for_url("**/main.php", timeout=5000)
        
        idx = "1479806"
        doc_url = f"https://www.my-auction.co.kr/view/pop_detail.php?type=mul&idx={idx}"
        print(f"Going to pop_detail page: {doc_url}")
        
        await page.goto(doc_url)
        await page.wait_for_timeout(2000)
        
        # Let's get raw bytes to decode manually
        html_bytes = await page.evaluate("document.documentElement.outerHTML")
        print("Raw outerHTML text:", html_bytes)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
