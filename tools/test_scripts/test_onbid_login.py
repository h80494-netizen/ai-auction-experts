import asyncio
from playwright.async_api import async_playwright

async def test_onbid_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print("온비드 로그인 페이지 접속...")
            # Go to login page
            await page.goto("https://www.onbid.co.kr/op/meminf/lgnmng/prtllgn/PrtlLgnController/main.do")
            await page.wait_for_timeout(2000)
            
            # Print title
            print("Title:", await page.title())
            
            # Fill login credentials
            print("로그인 폼 입력...")
            # Depending on how the form is laid out, there might be multiple login tabs.
            # Usually it's id or userid, pw or password
            await page.screenshot(path="onbid_login_before.png", full_page=True)
            
            # Usually there is an ID input and PW input
            # Let's dump all inputs
            inputs = await page.locator("input[type='text'], input[type='password']").all()
            for inp in inputs:
                try:
                    name = await inp.get_attribute('name')
                    id_attr = await inp.get_attribute('id')
                    print(f"Input Name: {name}, ID: {id_attr}")
                except:
                    pass
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_onbid_login())
