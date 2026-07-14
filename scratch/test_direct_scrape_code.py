import asyncio
from playwright.async_api import async_playwright
import os
import sys
from dotenv import load_dotenv

load_dotenv('backend/.env')
MYAUCTION_ID = os.getenv('MYAUCTION_ID')
MYAUCTION_PW = os.getenv('MYAUCTION_PW')

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("Navigating to login...")
        await page.goto('http://www.my-auction.co.kr/member/login.php')
        await page.fill('#id', MYAUCTION_ID)
        await page.fill('#passwd', MYAUCTION_PW)
        await page.click('#btn_login')
        await page.wait_for_url('**/main.php')
        print(f"Logged in, current URL: {page.url}")
        
        # Print form and search button HTML
        form_html = await page.locator("form[name='frm_top2']").evaluate("el => el.outerHTML")
        btn_html = await page.locator("#tk_btn").evaluate("el => el.outerHTML")
        print("\nForm HTML:")
        print(form_html)
        print("\nButton HTML:")
        print(btn_html)
        
        await browser.close()

asyncio.run(test())
