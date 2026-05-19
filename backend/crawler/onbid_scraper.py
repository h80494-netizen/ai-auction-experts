import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def download_gongmae_pdf(management_number: str, download_dir: str = "downloads") -> str:
    """
    온비드에 로그인하여 물건관리번호로 검색 후 공매재산명세서 PDF를 다운로드합니다.
    """
    os.makedirs(download_dir, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        try:
            print(f"[{management_number}] 온비드 메인 페이지 접속 중...")
            await page.goto("https://www.onbid.co.kr/op/meminf/lgnmng/prtllgn/PrtlLgnController/main.do", wait_until="networkidle")
            
            # 통합 검색창에 물건관리번호 입력 (force=True to bypass visibility checks if it's hidden behind a menu)
            print(f"물건관리번호({management_number}) 검색 중...")
            await page.locator("#mainSwd").fill(management_number, force=True)
            
            # 검색 버튼 클릭
            async with page.expect_navigation():
                await page.locator("#mainSwdBtn").click(force=True)
                
            print("검색 결과 페이지 이동 완료. 현재 URL:", page.url)
            await page.screenshot(path="onbid_search_result.png")
            
            # TODO: 검색 결과 목록에서 상세 페이지로 이동
            
            return "not_implemented_yet.pdf"
            
        except Exception as e:
            print(f"온비드 크롤링 중 오류 발생: {e}")
            await page.screenshot(path="onbid_error.png")
            raise e
        finally:
            await browser.close()

if __name__ == "__main__":
    import sys
    num = sys.argv[1] if len(sys.argv) > 1 else "2026-0400-023211"
    asyncio.run(download_gongmae_pdf(num))
