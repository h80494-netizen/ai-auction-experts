import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

async def run():
    load_dotenv()
    p = await async_playwright().start()
    b = await p.chromium.launch()
    c = await b.new_context()
    page = await c.new_page()
    await page.goto('https://www.my-auction.co.kr/member/login.php')
    await page.fill('#id', os.getenv('MYAUCTION_ID'))
    await page.fill('#passwd', os.getenv('MYAUCTION_PW'))
    await page.click('#btn_login')
    await page.wait_for_url('**/main.php')
    await page.goto('https://www.my-auction.co.kr/view/1394984')
    await page.wait_for_load_state('networkidle')
    html = await page.content()
    with open('dump.html', 'w', encoding='utf-8') as f:
        f.write(html)
    await b.close()

asyncio.run(run())
