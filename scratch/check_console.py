import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        page.on("console", lambda msg: print(f"CONSOLE {msg.type}: {msg.text}"))
        
        await page.goto('http://127.0.0.1:8000/map.html', wait_until='networkidle')
        await asyncio.sleep(2)
        
        try:
            await page.evaluate("document.getElementById('toggle-apt-info').checked = true;")
            await page.evaluate("toggleAptInfo()")
            await asyncio.sleep(3) # Wait for fetch and parsing
            num_layers = await page.evaluate("Object.keys(map._layers).length")
            print(f"Number of layers on map: {num_layers}")
        except Exception as e:
            print("toggleAptInfo Error:", e)
            
        await browser.close()

asyncio.run(main())
