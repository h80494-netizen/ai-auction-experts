import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        
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
            
            # Add global click listener to see what element is clicked
            await page.evaluate("""
                () => {
                    window.lastClickedElement = null;
                    document.addEventListener('click', (e) => {
                        const el = document.elementFromPoint(e.clientX, e.clientY);
                        console.log('CLICKED ELEMENT TAG:', el ? el.tagName : 'null');
                        console.log('CLICKED ELEMENT CLASS:', el ? el.className : 'null');
                        if (el && el.tagName.toLowerCase() === 'path') {
                            console.log('CLICKED A PATH!');
                        }
                        window.lastClickedElement = el ? (el.tagName + '.' + el.className) : 'null';
                    });
                }
            """)
            
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
            
            if center:
                # Physically click
                await page.mouse.click(center['x'], center['y'])
                await asyncio.sleep(1)
                
                clicked_info = await page.evaluate("window.lastClickedElement")
                print(f"ELEMENT UNDER CURSOR DURING CLICK: {clicked_info}")
                
        except Exception as e:
            print("ERROR:", e)
            
        await browser.close()

asyncio.run(main())
