import asyncio
from playwright.async_api import async_playwright

async def debug_onbid():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://www.onbid.co.kr')
        await page.wait_for_timeout(2000)
        
        try:
            async with context.expect_page(timeout=5000) as new_page_info:
                await page.evaluate("document.getElementById('mainSwd').value = '2024-0300-019349';")
                await page.evaluate("document.getElementById('mainSwdBtn').click();")
            
            new_page = await new_page_info.value
            await new_page.wait_for_load_state()
            print('New page URL:', new_page.url)
            
            html = await new_page.content()
            with open('onbid_new_page.html', 'w', encoding='utf-8') as f:
                f.write(html)
        except Exception as e:
            print("No new page opened:", e)
            print("Checking current page URL instead:", page.url)
            html = await page.content()
            with open('onbid_current_page.html', 'w', encoding='utf-8') as f:
                f.write(html)
        
        await browser.close()

asyncio.run(debug_onbid())
