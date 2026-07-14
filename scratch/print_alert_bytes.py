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
        
        alert_msg = ""
        
        async def handle_dialog(dialog):
            nonlocal alert_msg
            alert_msg = dialog.message
            print(f"Dialog received: {dialog.message}")
            await dialog.dismiss()
            
        page.on("dialog", handle_dialog)
        
        print(f"Logging in as {MYAUCTION_ID}...")
        await page.goto("https://www.my-auction.co.kr/member/login.php")
        await page.fill("#id", MYAUCTION_ID)
        await page.fill("#passwd", MYAUCTION_PW)
        await page.click("#btn_login")
        await page.wait_for_url("**/main.php", timeout=5000)
        
        idx = "1479806"
        doc_url = f"https://www.my-auction.co.kr/view/pop_detail.php?type=mul&idx={idx}"
        print(f"Going to pop_detail page: {doc_url}")
        
        # Navigate and expect dialog or navigation timeout due to alert blocking
        try:
            await page.goto(doc_url, wait_until="domcontentloaded", timeout=10000)
        except Exception as e:
            print("Navigation stopped (expected if alert blocks):", e)
            
        print("Alert text captured:")
        print(alert_msg)
        print("Alert text representation:", repr(alert_msg))
        
        # Save to file as utf-8
        with open("scratch/alert_message.txt", "w", encoding="utf-8") as f:
            f.write(alert_msg)
        print("Saved alert message to scratch/alert_message.txt")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
