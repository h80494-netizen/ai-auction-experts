import asyncio, os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()
MYAUCTION_ID = os.getenv('MYAUCTION_ID')
MYAUCTION_PW = os.getenv('MYAUCTION_PW')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://www.my-auction.co.kr/member/login.php')
        await page.fill('#id', MYAUCTION_ID)
        await page.fill('#passwd', MYAUCTION_PW)
        await page.click('#btn_login')
        await page.wait_for_timeout(2000)
        
        await page.goto('https://www.my-auction.co.kr/auction/search.php')
        
        # Use top form
        await page.select_option("form[name='frm_top2'] select[name='sno']", "2024")
        await page.locator("form[name='frm_top2'] input[name='tno']").fill("5020")
        
        # click top search
        await page.click("#tk_btn a")
        
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)
        
        print("URL after search:", page.url)
        await page.screenshot(path="search_screenshot.png")
        
        html = await page.content()
        with open("search_table2.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Done")
        await browser.close()

asyncio.run(main())
