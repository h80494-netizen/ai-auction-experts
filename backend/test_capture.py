import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

load_dotenv()
MYAUCTION_ID = os.getenv("MYAUCTION_ID")
MYAUCTION_PW = os.getenv("MYAUCTION_PW")

async def test_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://www.my-auction.co.kr/member/login.php")
        await page.fill("#id", MYAUCTION_ID)
        await page.fill("#passwd", MYAUCTION_PW)
        await page.click("#btn_login")
        await page.wait_for_url("**/main.php")
        
        # 사건 1394984 (2024타경5020) 이동
        await page.goto("https://www.my-auction.co.kr/view/1394984")
        await page.wait_for_load_state('networkidle')
        
        os.makedirs("test_images", exist_ok=True)
        
        try:
            # 1. 썸네일 이미지 (전경 및 구조도)
            # 마이옥션 썸네일 구조 파악
            thumbs = page.locator(".con_L .photo_list ul li img")
            count = await thumbs.count()
            print(f"발견된 썸네일 이미지 수: {count}")
            for i in range(min(count, 3)):
                await thumbs.nth(i).screenshot(path=f"test_images/thumb_{i}.png")
                print(f"썸네일 {i} 캡쳐 완료")
        except Exception as e:
            print("썸네일 캡쳐 실패:", e)

        try:
            # 2. 카카오맵 캡쳐
            # 지도가 있는 컨테이너를 찾아 캡쳐 (보통 .map_area 또는 iframe)
            map_elem = page.locator("#map")
            if await map_elem.count() > 0:
                await map_elem.screenshot(path="test_images/map.png")
                print("지도 캡쳐 완료")
            else:
                print("지도를 찾을 수 없습니다.")
        except Exception as e:
            print("지도 캡쳐 실패:", e)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_screenshot())
