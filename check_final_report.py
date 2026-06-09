import asyncio
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.launch()
    page = await browser.new_page()
    
    errors = []
    page.on('pageerror', lambda e: errors.append(f'PAGE_ERROR: {e}'))
    page.on('console', lambda msg: errors.append(f'CONSOLE: {msg.text}') if msg.type == 'error' else None)
    
    await page.goto('http://localhost:8000/')
    
    # Login through the overlay
    await page.fill('#passwordInput', '1234')
    await page.click('#loginBtn')
    await page.wait_for_selector('#loginOverlay.hidden')
    
    await page.fill('#caseNumberInput', '2024타경62469')
    await page.click('#searchCaseBtn')
    
    # Wait for search to complete (address list appears)
    await page.wait_for_selector('.address-btn', timeout=60000)
    
    # Click the first address to select it
    await page.click('.address-btn')
    
    # Click start button
    await page.click('#startBtn')
    
    # Wait for analysis to complete (finalReport becomes visible)
    try:
        await page.wait_for_selector('#finalReport:not(.hidden)', timeout=30000)
        print("Analysis completed successfully!")
    except Exception as e:
        print("Timeout waiting for final report!")
        
    for err in errors:
        print(err)
        
    await browser.close()
    await p.stop()

asyncio.run(main())
