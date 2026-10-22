import asyncio
from playwright.async_api import async_playwright

MADANGS_ID = "h80494"
MADANGS_PW = "spring11!!"

async def test_madangs_search(case_number: str):
    clean_case = case_number.replace("-", "")
    target_url = f"https://madangs.com/goview?g_code={clean_case}"
    print(f"[{case_number}] 마당스 검색 시도: {target_url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # Login first
            print("로그인 페이지 이동...")
            await page.goto("https://madangs.com/login", wait_until="domcontentloaded", timeout=10000)
            
            # We need to find the login form selectors
            # Trying standard names or we can just try without login first
            
            await page.fill("input[name='id']", MADANGS_ID)
            await page.fill("input[name='password']", MADANGS_PW)
            # Try to click login button
            await page.click("button:has-text('로그인'), input[type='submit']")
            await page.wait_for_timeout(2000)
        except Exception as e:
            print(f"Login form error (maybe already logged in or different selectors): {e}")

        try:
            print(f"상세 페이지 이동: {target_url}")
            await page.goto(target_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            with open("madangs_result.html", "w", encoding="utf-8") as f:
                f.write(html)
                
            await page.screenshot(path="madangs_direct_search.png", full_page=True)
            
            # Check if there is actual data or an error message like "No data"
            text_content = await page.locator("body").inner_text()
            if "결과가 없습니다" in text_content or "존재하지 않는" in text_content:
                print("마당스에도 해당 데이터가 존재하지 않습니다.")
            else:
                print(f"페이지 텍스트 길이: {len(text_content)}")
                print("성공적으로 데이터를 로드했을 가능성이 있습니다.")
                print(text_content[:500].replace('\n', ' '))
                
        except Exception as e:
            print(f"Error fetching detail page: {e}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_madangs_search("2025-0800-059271"))
