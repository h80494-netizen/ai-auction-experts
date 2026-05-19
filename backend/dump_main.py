import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

async def dump_main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        await page.goto("https://www.my-auction.co.kr/member/login.php")
        await page.fill("#id", os.getenv("MYAUCTION_ID"))
        await page.fill("#passwd", os.getenv("MYAUCTION_PW"))
        await page.click("#btn_login")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(10000)
        print("Current URL:", page.url)
        
        # main.php의 HTML을 파일로 덤프
        html = await page.content()
        with open("main_dump.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        print("main.php 덤프 완료!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(dump_main())
