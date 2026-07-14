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
            
            # Check Z-Index and DOM order of Overlay Pane children
            order_info = await page.evaluate("""
                () => {
                    const pane = document.querySelector('.leaflet-overlay-pane');
                    if (!pane) return 'No overlay pane';
                    const children = Array.from(pane.children).map(c => {
                        const style = window.getComputedStyle(c);
                        return `${c.tagName}(zIndex: ${style.zIndex}, pointerEvents: ${style.pointerEvents}, width: ${style.width}, height: ${style.height})`;
                    });
                    return children.join(' | ');
                }
            """)
            print(f"OVERLAY PANE CHILDREN: {order_info}")
            
        except Exception as e:
            print("ERROR:", e)
            
        await browser.close()

asyncio.run(main())
