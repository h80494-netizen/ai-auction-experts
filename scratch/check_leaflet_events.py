import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        page.on("console", lambda msg: print(f"CONSOLE {msg.type}: {msg.text}"))
        
        await page.goto('http://127.0.0.1:8000/map.html', wait_until='networkidle')
        await asyncio.sleep(2)
        
        try:
            await page.evaluate("document.getElementById('toggle-apt-info').checked = true;")
            await page.evaluate("toggleAptInfo()")
            await asyncio.sleep(3) # Wait for fetch and parsing
            
            # Get the first layer and fire a click event on it
            res = await page.evaluate("""
                () => {
                    const layers = Object.values(aptInfoLayer._layers);
                    if (layers.length > 0) {
                        const firstLayer = layers[0];
                        firstLayer.fire('click');
                        return document.querySelector('.leaflet-popup-content') ? document.querySelector('.leaflet-popup-content').innerHTML : 'No popup';
                    }
                    return 'No layers';
                }
            """)
            print(f"Popup Content: {res}")
            
            # Fire mouseover to trigger tooltip
            tooltip_res = await page.evaluate("""
                () => {
                    const layers = Object.values(aptInfoLayer._layers);
                    if (layers.length > 0) {
                        const firstLayer = layers[0];
                        firstLayer.fire('mouseover');
                        return document.querySelector('.leaflet-tooltip') ? document.querySelector('.leaflet-tooltip').innerHTML : 'No tooltip';
                    }
                    return 'No layers';
                }
            """)
            print(f"Tooltip Content: {tooltip_res}")
            
        except Exception as e:
            print("Error:", e)
            
        await browser.close()

asyncio.run(main())
