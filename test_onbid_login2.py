import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        print("Visiting login page...")
        await page.goto('https://www.onbid.co.kr/op/meminf/lgnmng/prtllgn/loginForm.do')
        await page.wait_for_timeout(2000)
        
        # Take a screenshot to see what it looks like
        await page.screenshot(path="onbid_login_page.png", full_page=True)
        html = await page.content()
        with open('onbid_login_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Done")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
