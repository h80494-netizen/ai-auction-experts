import asyncio
from playwright.async_api import async_playwright
import os

MYAUCTION_ID = "h80494"
MYAUCTION_PW = "spring11!!"

async def test_search():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://www.my-auction.co.kr/member/login.php", wait_until="domcontentloaded", timeout=10000)
        await page.fill("#id", MYAUCTION_ID)
        await page.fill("#passwd", MYAUCTION_PW)
        await page.click("#btn_login")
        await page.wait_for_load_state("domcontentloaded")
        
        await page.goto('https://www.my-auction.co.kr/auction/public.php')
        await page.wait_for_timeout(1000)
        
        # Test 1: without hyphens
        await page.fill("input[name='cltr_mnmt_no']", "20250800059271")
        async with page.expect_navigation(timeout=10000):
            await page.click("form[name='frm'] button:has-text('검색')")
            
        rows = page.locator("table.tbl_auction_list tbody tr, table.tbl_auction_list tr")
        count = await rows.count()
        print(f"Without hyphens: Found {count} rows")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_search())
