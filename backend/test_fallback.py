import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.my-auction.co.kr/member/login.php")
        await page.fill("#id", os.getenv("MYAUCTION_ID"))
        await page.fill("#passwd", os.getenv("MYAUCTION_PW"))
        await page.click("#btn_login")
        await page.wait_for_url("**/main.php", timeout=5000)
        
        # main.php에서 2024 5020 검색
        await page.select_option("form[name='frm_top2'] select[name='sno']", "2024")
        await page.locator("form[name='frm_top2'] input[name='tno']").fill("5020")
        await page.click("#tk_btn a")
        
        try:
            await page.wait_for_url("**/search_list.php", timeout=5000)
        except Exception as e:
            print("Failed to navigate to search_list.php:", e)
            
        await page.wait_for_timeout(1000)
        
        # 첫 번째 링크 가져오기
        link = page.locator("a[href*='/view/'], .result-list a, .list-table a").first
        print("First link:", await link.get_attribute("href"))
        
        # 이동해서 상세 정보 파싱
        full_url = await link.get_attribute("href")
        if not full_url.startswith("http"):
            full_url = "https://www.my-auction.co.kr" + full_url
        await page.goto(full_url)
        await page.wait_for_load_state("networkidle")
        
        html = await page.content()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        address = ""
        for th in soup.find_all("th"):
            if "소재지" in th.text:
                td = th.find_next_sibling("td")
                if td:
                    address = td.text.strip()
                    break
        print("Address of the first link:", address)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test())
