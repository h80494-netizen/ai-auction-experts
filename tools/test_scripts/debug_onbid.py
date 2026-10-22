import asyncio
from playwright.async_api import async_playwright

async def debug_onbid():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://www.onbid.co.kr')
        await page.wait_for_timeout(2000)
        
        await page.evaluate("document.getElementById('mainSwd').value = '2024-0300-019349';")
        await page.evaluate("document.getElementById('mainSwdBtn').click();")
        await page.wait_for_timeout(5000)
        
        await page.screenshot(path='onbid_search_result.png')
        print('Screenshot saved to onbid_search_result.png')
        
        html = await page.content()
        with open('onbid_search_result.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print('HTML saved')
        
        await browser.close()

asyncio.run(debug_onbid())
