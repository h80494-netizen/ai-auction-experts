import asyncio
from playwright.async_api import async_playwright

async def search_onbid_directly(case_number: str):
    print(f"[{case_number}] 온비드 직접 검색 시도...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            await page.goto("https://www.onbid.co.kr/op/meminf/lgnmng/prtllgn/PrtlLgnController/main.do")
            await page.wait_for_timeout(2000)
            
            # Close popups if any
            popups = page.locator(".btn_close")
            count = await popups.count()
            for i in range(count):
                try: await popups.nth(i).click(timeout=1000)
                except: pass
                
            await page.fill("#mainSwd", case_number)
            async with page.expect_navigation():
                await page.click("#mainSwdBtn")
                
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(3000)
            
            # Capture what Onbid says
            result_text = await page.locator("body").inner_text()
            print("Onbid Result Length:", len(result_text))
            
            if "결과가 없습니다" in result_text or "검색결과 0건" in result_text:
                print("온비드에서도 검색결과가 없습니다.")
            else:
                print("온비드에서는 검색결과가 존재합니다!")
                
            await page.screenshot(path="onbid_direct_search.png", full_page=True)
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(search_onbid_directly("2025-0800-059271"))
