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
        page = await browser.new_page()
        await page.goto('https://www.my-auction.co.kr/member/login.php')
        await page.fill('#id', MYAUCTION_ID)
        await page.fill('#passwd', MYAUCTION_PW)
        await page.click('#btn_login')
        await page.wait_for_timeout(2000)
        
        # Test direct access
        target = 'cltr_mnmt_no=2024-0100-008372'
        encoded = base64.b64encode(target.encode()).decode()
        url = f'https://www.my-auction.co.kr/auction/detail_public.php?idxpu={encoded}||'
        print('Going to:', url)
        
        await page.goto(url)
        await page.wait_for_timeout(2000)
        
        text = await page.content()
        with open('public_detail.html', 'w', encoding='utf-8') as f:
            f.write(text)
            
        print('Length:', len(text))
        
        # Look for PDF links
        links = await page.locator('a:has-text("감정평가서"), a:has-text("재산명세서"), a:has-text("공고문")').all()
        for link in links:
            print('PDF link:', await link.get_attribute('href'), await link.inner_text())
            
        await browser.close()

asyncio.run(main())
