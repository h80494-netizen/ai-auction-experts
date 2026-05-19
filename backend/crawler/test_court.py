import asyncio
from playwright.async_api import async_playwright

async def test_court_auction():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        
        try:
            await page.goto("https://www.courtauction.go.kr/", wait_until="networkidle")
            await page.wait_for_timeout(2000)
            
            # Print all frames
            for frame in page.frames:
                print(f"Frame URL: {frame.url}, Name: {frame.name}")
                
            # Usually the main content is in a frame named 'indexFrame'
            index_frame = page.frame(name="indexFrame")
            if not index_frame:
                index_frame = page.main_frame
                
            print("Trying to find search inputs in indexFrame or main_frame...")
            
            # Print some HTML to understand structure
            content = await index_frame.content()
            print(f"Content length: {len(content)}")
            
            # Try to search for case 2024타경5020 (Usually courtauction requires court name + case number)
            # Supreme court auction requires selecting the court from a dropdown, then entering year and number.
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_court_auction())
