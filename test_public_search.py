import asyncio
from playwright.async_api import async_playwright
import os

MYAUCTION_ID = "h80494"
MYAUCTION_PW = "spring11!!"

async def search_myauction_list(case_number: str):
    clean_case = case_number.replace(" ", "")
    is_public_sale = "-" in clean_case
    print(f"[{case_number}] Search starting. Public Sale: {is_public_sale}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://www.my-auction.co.kr/member/login.php", wait_until="domcontentloaded", timeout=10000)
        await page.fill("#id", MYAUCTION_ID)
        await page.fill("#passwd", MYAUCTION_PW)
        await page.click("#btn_login")
        await page.wait_for_load_state("domcontentloaded")
        
        if is_public_sale:
            await page.goto('https://www.my-auction.co.kr/auction/public.php')
            await page.wait_for_timeout(1000)
            await page.fill("input[name='cltr_mnmt_no']", clean_case)
            
            # Click search button
            async with page.expect_navigation(timeout=10000):
                await page.click("form[name='frm'] button:has-text('검색')")
        
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(2000)
        
        await page.screenshot(path="public_search.png", full_page=True)
        
        rows = page.locator("table.tbl_auction_list tbody tr, table.tbl_auction_list tr")
        count = await rows.count()
        print(f"Found {count} rows")
        
        for i in range(count):
            row_text = await rows.nth(i).inner_text()
            print(f"Row {i}: {row_text[:100]}...")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(search_myauction_list("2025-0800-059271"))
