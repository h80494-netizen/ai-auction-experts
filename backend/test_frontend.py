import asyncio
from playwright.async_api import async_playwright

async def test_frontend():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Listen for all console events and print them
        page.on("console", lambda msg: print(f"CONSOLE {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
        
        # Open the local HTML file
        await page.goto(r"file:///c:/Users/llll/Documents/두인경매/바이브코딩/public/index.html")
        
        # Wait a bit
        await asyncio.sleep(1)
        
        # Try to type into the input and click the search button
        print("Typing case number...")
        await page.fill("#caseNumberInput", "2024타경5020")
        print("Clicking searchCaseBtn...")
        await page.click("#searchCaseBtn")
        
        # Wait a bit to see if anything happens
        await asyncio.sleep(2)
        print("Test finished.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_frontend())
