import asyncio
from playwright.async_api import async_playwright

MADANGS_ID = "h80494"
MADANGS_PW = "spring11!!"

async def login_and_dump_madangs(g_code: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("로그인 페이지 이동...")
            await page.goto("https://madangs.com/member/login")
            
            await page.fill("input[name='id'], input[name='user_id'], input[type='text']", MADANGS_ID)
            await page.fill("input[type='password']", MADANGS_PW)
            await page.press("input[type='password']", "Enter")
            await page.wait_for_load_state("networkidle", timeout=5000)
            
            print(f"상세 페이지 이동: https://madangs.com/goview?g_code={g_code}")
            await page.goto(f"https://madangs.com/goview?g_code={g_code}", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            with open("madangs_logged_in.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Done")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(login_and_dump_madangs("202402402003"))
