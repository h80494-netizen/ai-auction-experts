import asyncio
from playwright.async_api import async_playwright
import os
import base64
from dotenv import load_dotenv

load_dotenv('backend/.env')

MYAUCTION_ID = os.getenv('MYAUCTION_ID')
MYAUCTION_PW = os.getenv('MYAUCTION_PW')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://www.my-auction.co.kr/member/login.php')
        await page.fill('#id', MYAUCTION_ID)
        await page.fill('#passwd', MYAUCTION_PW)
        await page.click('#btn_login')
        await page.wait_for_timeout(2000)
        
        target = 'cltr_mnmt_no=2024-0100-008372'
        encoded = base64.b64encode(target.encode()).decode()
        url = f'https://www.my-auction.co.kr/auction/detail_public.php?idxpu={encoded}||'
        await page.goto(url)
        await page.wait_for_timeout(2000)
        
        # Click the Appraisal Report link and capture the new page/popup
        # Click the Appraisal Report link and capture the new page/popup
        try:
            async with context.expect_page() as new_page_info:
                await page.click('a:has-text("감정평가서")')
            new_page = await new_page_info.value
            await new_page.wait_for_load_state()
            await new_page.wait_for_timeout(3000)
            
            frame_html = await new_page.frame_locator('iframe#detail_target').locator('body').inner_html()
            print('Frame HTML length:', len(frame_html))
            with open('iframe_fetched.html', 'w', encoding='utf-8') as f:
                f.write(frame_html)
        except Exception as e:
            print('Failed to click or get page:', e)
        
        await browser.close()

asyncio.run(main())
