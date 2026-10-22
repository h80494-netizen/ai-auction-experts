import asyncio
from playwright.async_api import async_playwright

async def test_madangs_search(case_number: str):
    clean_case = case_number.replace("-", "")
    target_url = f"https://madangs.com/goview?g_code={clean_case}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            await page.goto(target_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            # 텍스트 가져오기 (이모지 제거 등 안전하게 출력)
            text_content = await page.locator("body").inner_text()
            print(text_content.encode('utf-8', 'ignore').decode('utf-8')[:1000])
                
        except Exception as e:
            pass
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_madangs_search("2025-0800-059271"))
