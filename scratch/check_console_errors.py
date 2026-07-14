import sys
import asyncio

async def main():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Playwright is not installed. Let's try to install it or use Selenium.")
        import subprocess
        subprocess.run(["pip", "install", "playwright"])
        subprocess.run(["playwright", "install", "chromium"])
        from playwright.async_api import async_playwright
        
    print("Launching browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: console_logs.append(f"[ERROR] {err.message}"))
        
        url = "http://localhost:8000/map.html?v=1"
        print(f"Navigating to {url}...")
        try:
            await page.goto(url, wait_until="networkidle", timeout=10000)
        except Exception as e:
            print("Navigation timed out or failed:", e)
            
        print("Waiting 3 seconds...")
        await asyncio.sleep(3)
        
        print("\n--- Console Logs ---")
        for log in console_logs:
            print(log)
            
        # Check if L is defined, or if map is initialized, or if there's a stuck overlay
        try:
            eval_res = await page.evaluate("() => { return { L_defined: typeof L !== 'undefined', map_defined: typeof map !== 'undefined', loading_display: document.getElementById('loading').style.display }; }")
            print("\nPage JavaScript Variables:", eval_res)
        except Exception as e:
            print("Failed to evaluate JS variables:", e)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
