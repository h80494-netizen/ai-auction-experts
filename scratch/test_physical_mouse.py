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
            # Turn on APT info
            await page.evaluate("document.getElementById('toggle-apt-info').checked = true;")
            await page.evaluate("toggleAptInfo()")
            await asyncio.sleep(3)
            
            # Pan map to the first polygon
            await page.evaluate("""
                () => {
                    const layers = Object.values(aptInfoLayer._layers);
                    if (layers.length > 0) {
                        const firstLayer = layers[0];
                        map.fitBounds(firstLayer.getBounds());
                    }
                }
            """)
            await asyncio.sleep(2)
            
            # Find the exact pixel coordinates of the first polygon AFTER panning
            center = await page.evaluate("""
                () => {
                    const layers = Object.values(aptInfoLayer._layers);
                    if (layers.length > 0) {
                        const firstLayer = layers[0];
                        const center = firstLayer.getBounds().getCenter();
                        const pt = map.latLngToContainerPoint(center);
                        const mapRect = document.getElementById('map').getBoundingClientRect();
                        return {x: pt.x + mapRect.left, y: pt.y + mapRect.top};
                    }
                    return null;
                }
            """)
            print(f"Polygon center pixels: {center}")
            
            if center:
                # Physically move the mouse
                await page.mouse.move(center['x'], center['y'])
                await asyncio.sleep(1)
                
                # Check if tooltip exists in DOM
                tt = await page.evaluate("document.querySelector('.leaflet-tooltip') ? document.querySelector('.leaflet-tooltip').innerText : 'No tooltip'")
                print(f"PHYSICAL HOVER TOOLTIP: {tt}")
                
                # Physically click
                await page.mouse.click(center['x'], center['y'])
                await asyncio.sleep(1)
                
                pp = await page.evaluate("document.querySelector('.leaflet-popup-content') ? document.querySelector('.leaflet-popup-content').innerText : 'No popup'")
                print(f"PHYSICAL CLICK POPUP: {pp}")
                
        except Exception as e:
            print("ERROR:", e)
            
        await browser.close()

asyncio.run(main())
