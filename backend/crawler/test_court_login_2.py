import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("Going to courtauction...")
            await page.goto("https://www.courtauction.go.kr/")
            # Login action on court auction usually requires submitting a form to Login.ok or clicking a button.
            # Court auction login requires frame 'indexFrame'.
            # Wait, there's a login link: <img src="/images/main/btn_login.gif">
            # I can just navigate directly to the login page:
            await page.goto("https://www.courtauction.go.kr/MemberLogin.ok")
            await page.wait_for_timeout(2000)
            
            # The login page has input name="id" and "password"
            await page.fill("input[name='id']", "h804949")
            await page.fill("input[name='password']", "spring11!!")
            await page.click("a:has(img[src*='btn_login'])")
            
            await page.wait_for_timeout(3000)
            
            # Check if login success
            content = await page.content()
            if "h804949" in content or "로그아웃" in content:
                print("Login SUCCESS!")
            else:
                print("Login FAILED or CAPTCHA.")
                
        except Exception as e:
            print("Error:", e)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
