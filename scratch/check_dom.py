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
            
            # Check DOM for SVG paths and their pointer-events
            svg_info = await page.evaluate("""
                () => {
                    const paths = document.querySelectorAll('path');
                    if (paths.length === 0) return 'No paths found in DOM';
                    const path = paths[0];
                    const style = window.getComputedStyle(path);
                    return `Found ${paths.length} paths. pointer-events: ${style.pointerEvents}, stroke: ${style.stroke}, fill: ${style.fill}, isConnected: ${path.isConnected}`;
                }
            """)
            print(f"SVG INFO: {svg_info}")
            
            # Check Canvas
            canvas_info = await page.evaluate("""
                () => {
                    const canvases = document.querySelectorAll('canvas');
                    return `Found ${canvases.length} canvases.`;
                }
            """)
            print(f"CANVAS INFO: {canvas_info}")
            
        except Exception as e:
            print("ERROR:", e)
            
        await browser.close()

asyncio.run(main())
