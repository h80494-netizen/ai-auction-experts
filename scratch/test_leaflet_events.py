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
            # Turn on APT info
            await page.evaluate("document.getElementById('toggle-apt-info').checked = true;")
            await page.evaluate("toggleAptInfo()")
            await asyncio.sleep(3)
            
            # Fire mouseover and check tooltip
            tooltip_text = await page.evaluate("""
                () => {
                    const layers = Object.values(aptInfoLayer._layers);
                    if (layers.length > 0) {
                        const firstLayer = layers[0];
                        firstLayer.fire('mouseover');
                        const tt = document.querySelector('.leaflet-tooltip');
                        return tt ? tt.innerText : 'No tooltip';
                    }
                    return 'No layers';
                }
            """)
            print(f"TOOLTIP: {tooltip_text}")
            
            # Fire click and check popup
            popup_text = await page.evaluate("""
                () => {
                    const layers = Object.values(aptInfoLayer._layers);
                    if (layers.length > 0) {
                        const firstLayer = layers[0];
                        firstLayer.fire('click');
                        const pp = document.querySelector('.leaflet-popup-content');
                        return pp ? pp.innerText : 'No popup';
                    }
                    return 'No layers';
                }
            """)
            print(f"POPUP: {popup_text}")
            
        except Exception as e:
            print("ERROR:", e)
            
        await browser.close()

asyncio.run(main())
