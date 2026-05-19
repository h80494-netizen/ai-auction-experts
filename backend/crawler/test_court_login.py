import asyncio
from playwright.async_api import async_playwright

async def login_and_search():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        
        try:
            await page.goto("https://www.courtauction.go.kr/", wait_until="networkidle")
            
            # Click Login button
            await page.click("a[href*='login.jsp']")
            await page.wait_for_timeout(2000)
            
            # Find main frame
            frame = page.frame(name="indexFrame")
            if not frame:
                frame = page.main_frame
            
            # Fill login
            await frame.fill("input#id", "h804949")
            await frame.fill("input#password", "spring11!!")
            await frame.click("a[href*='loginAction()']")
            
            await page.wait_for_timeout(3000)
            
            print("Login completed. Current URL:", page.url)
            
            # Now we need to search for a case. For supreme court, we usually need the Court Name + Case Year + Case Number.
            # Example: 2024타경5020. Which court is it? Supreme court search requires the exact court name (e.g. 서울중앙지방법원).
            # This makes generic searching by only '2024타경5020' impossible without iterating through all courts.
            print("Search requires Court Name on the Supreme Court site.")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(login_and_search())
