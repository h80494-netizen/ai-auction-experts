import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.my-auction.co.kr/member/login.php")
        await page.fill("#id", os.getenv("MYAUCTION_ID"))
        await page.fill("#passwd", os.getenv("MYAUCTION_PW"))
        await page.click("#btn_login")
        await page.wait_for_url("**/main.php", timeout=5000)
        
        await page.goto("https://www.my-auction.co.kr/view/pop_detail.php?type=mul&idx=1394984")
        print("URL:", page.url)
        html = await page.content()
        print(html[:500])
        
        import base64
        # check if it's pdf content
        if "%PDF" in html[:10]:
            print("It is a raw PDF file!")
        else:
            print("It is an HTML page.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test())
