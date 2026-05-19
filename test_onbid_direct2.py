import asyncio
from playwright.async_api import async_playwright

async def search_onbid_directly(case_number: str):
    print(f"[{case_number}] 온비드 직접 검색 시도...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            await page.goto("https://www.onbid.co.kr/op/meminf/lgnmng/prtllgn/PrtlLgnController/main.do", wait_until="networkidle")
            await page.wait_for_timeout(2000)
            
            # Fill hidden search box using force=True
            await page.locator("#mainSwd").fill(case_number, force=True)
            
            async with page.expect_navigation():
                await page.locator("#mainSwdBtn").click(force=True)
                
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(3000)
            
            # Now we are on the search result page.
            # Look for the table with results
            print("현재 URL:", page.url)
            
            # Dump all tables
            tables = await page.locator("table").all()
            print(f"테이블 {len(tables)}개 발견")
            for i, tbl in enumerate(tables):
                text = await tbl.inner_text()
                print(f"--- 테이블 {i} ---")
                print(text[:200].encode('utf-8'))
                
            await page.screenshot(path="onbid_direct_search2.png", full_page=True)
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(search_onbid_directly("2025-0800-059271"))
