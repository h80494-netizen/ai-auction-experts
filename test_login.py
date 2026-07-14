import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv('backend/.env')
MYAUCTION_ID = os.environ.get('MYAUCTION_ID')
MYAUCTION_PW = os.environ.get('MYAUCTION_PW')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        async def handle_dialog(dialog):
            print(f"Alert: {dialog.message}")
            await dialog.dismiss()
        page.on("dialog", handle_dialog)
        
        print(f"Login as {MYAUCTION_ID}")
        await page.goto("http://www.my-auction.co.kr/member/login.php")
        await page.fill("#id", MYAUCTION_ID)
        await page.fill("#passwd", MYAUCTION_PW)
        await page.click("#btn_login")
        await page.wait_for_load_state('networkidle')
        
        await page.screenshot(path="login_after.png")
        print("Current URL:", page.url)
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
