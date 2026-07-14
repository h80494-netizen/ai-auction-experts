import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Log all console events
        def handle_console(msg):
            print(f"[BROWSER CONSOLE] {msg.type}: {msg.text}")
        page.on("console", handle_console)
        
        # Open the dashboard with a case parameter
        print("Navigating to dashboard...")
        await page.goto("http://localhost:8000/?case=2024%20%ED%83%80%EA%B2%BD%206008")
        
        # Wait for overlay to appear
        print("Waiting for login overlay...")
        await page.wait_for_timeout(1000)
        
        # Enter password and login
        try:
            print("Entering password...")
            await page.fill("#passwordInput", "1234")
            await page.click("#loginBtn")
            print("Login button clicked.")
        except Exception as e:
            print("Login overlay not found or error:", e)
            
        # Wait for search and potential analysis (30 seconds to allow scraping and analysis to proceed)
        print("Waiting 30 seconds for search and analysis flow...")
        await page.wait_for_timeout(30000)
        
        # Check if the spinner is visible
        loading_visible = await page.locator("#loadingState").is_visible()
        start_btn_disabled = await page.locator("#startBtn").is_disabled()
        final_report_visible = await page.locator("#finalReport").is_visible()
        
        print(f"loadingState visible: {loading_visible}")
        print(f"startBtn disabled: {start_btn_disabled}")
        print(f"finalReport visible: {final_report_visible}")
        
        # Take a screenshot to verify
        await page.screenshot(path="scratch/test_result.png")
        print("Screenshot saved to scratch/test_result.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
