import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        
        page.on("console", lambda msg: print(f"CONSOLE {msg.type}: {msg.text}"))
        
        await page.goto('http://127.0.0.1:8000/map.html', wait_until='networkidle')
        await asyncio.sleep(2)
        
        try:
            # Check the box to load polygons
            await page.evaluate("document.getElementById('toggle-apt-info').checked = true;")
            await page.evaluate("toggleAptInfo()")
            await asyncio.sleep(3)
            
            # Fire mouseover to trigger tooltip on the first polygon
            await page.evaluate("""
                () => {
                    const layers = Object.values(aptInfoLayer._layers);
                    if (layers.length > 0) {
                        const firstLayer = layers[0];
                        // Fire mouseover
                        firstLayer.fire('mouseover');
                        // Get bounds to hover mouse exactly there
                        const center = firstLayer.getBounds().getCenter();
                        return {lat: center.lat, lng: center.lng};
                    }
                    return null;
                }
            """)
            
            # Take screenshot to see if polygons and tooltip exist
            await page.screenshot(path='c:/Users/llll/Documents/두인경매/바이브코딩/scratch/debug_hover.png')
            print("Saved screenshot to debug_hover.png")
            
            # Now click it
            await page.evaluate("""
                () => {
                    const layers = Object.values(aptInfoLayer._layers);
                    if (layers.length > 0) {
                        const firstLayer = layers[0];
                        firstLayer.fire('click');
                    }
                }
            """)
            await asyncio.sleep(1)
            await page.screenshot(path='c:/Users/llll/Documents/두인경매/바이브코딩/scratch/debug_click.png')
            print("Saved screenshot to debug_click.png")
            
        except Exception as e:
            print("Error:", e)
            
        await browser.close()

asyncio.run(main())
