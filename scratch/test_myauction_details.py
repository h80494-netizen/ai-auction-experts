import asyncio
import os
import re
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env')
load_dotenv(dotenv_path=env_path)

MYAUCTION_ID = os.getenv("MYAUCTION_ID", "lgs3397")
MYAUCTION_PW = os.getenv("MYAUCTION_PW", "3397lgs")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("Logging in to MyAuction...")
        await page.goto("https://www.my-auction.co.kr/member/login.php")
        await page.fill("#id", MYAUCTION_ID)
        await page.fill("#passwd", MYAUCTION_PW)
        await page.click("#btn_login")
        await page.wait_for_url("**/main.php", timeout=5000)
        print("Login successful. URL:", page.url)
        
        # Search for 2025 타경 100709
        print("Searching for case 2025 타경 100709...")
        await page.goto("https://www.my-auction.co.kr/auction/search.php")
        await page.select_option("form[name='frm'] select[name='sno']", "2025")
        await page.locator("form[name='frm'] input[name='tno']").fill("100709")
        
        async with page.expect_navigation(timeout=10000):
            await page.click("form[name='frm'] button:has-text('검색')")
            
        print("Search complete. URL:", page.url)
        
        # Click search result
        found_link = page.locator("a[href*='/view/'], a[href*='idx='], .result-list a, .list-table a").first
        if await found_link.count() > 0:
            href = await found_link.get_attribute("href")
            full_url = href if href.startswith("http") else f"https://www.my-auction.co.kr{href}"
            print("Found detail link:", full_url)
            await page.goto(full_url)
            await page.wait_for_load_state('networkidle')
            print("Detail page URL:", page.url)
            
            # Find idx
            idx_match = re.search(r'/view/(\d+)', page.url) or re.search(r'idx=(\d+)', page.url)
            idx = idx_match.group(1) if idx_match else None
            print("Case idx:", idx)
            
            # Evaluate pop_detail.toString() to inspect the javascript definition
            try:
                js_definition = await page.evaluate("() => typeof pop_detail !== 'undefined' ? pop_detail.toString() : 'pop_detail is undefined'")
                print("=== JAVASCRIPT pop_detail DEFINITION ===")
                print(js_definition)
            except Exception as js_err:
                print(f"Failed to evaluate pop_detail: {js_err}")
            
            # Scan popup triggers
            print("=== SCANNING FOR POPUP BUTTONS/LINKS ===")
            popup_elements = page.locator("a[href*='pop_detail'], [onclick*='pop_detail'], a[href*='windowOpen'], [onclick*='windowOpen'], a:has-text('명세서'), a:has-text('조사서'), a:has-text('평가서'), a:has-text('등기'), a:has-text('대장')")
            el_count = await popup_elements.count()
            print(f"Found {el_count} potential popup links.")
            for i in range(el_count):
                txt = await popup_elements.nth(i).inner_text()
                href = await popup_elements.nth(i).get_attribute("href")
                onclick = await popup_elements.nth(i).get_attribute("onclick")
                print(f"[{i}] text: '{txt.strip()}', href: '{href}', onclick: '{onclick}'")

            # Dump tenant section from details page html
            detail_html = await page.content()
            soup = BeautifulSoup(detail_html, 'html.parser')
            
            print("=== SEARCHING FOR TENANT STATUS TABLE IN MAIN HTML ===")
            tenant_tables = soup.find_all(lambda tag: tag.name == 'table' and ('임차인' in tag.text or '전입일자' in tag.text or '보증금' in tag.text))
            print(f"Found {len(tenant_tables)} potential tenant tables in main HTML.")
            for i, tbl in enumerate(tenant_tables[:3]):
                print(f"\n--- Potential Tenant Table {i} (first 800 chars) ---")
                print(str(tbl)[:800])
            
            # Let's inspect pop_detail.php?type=mul&idx=...
            if idx:
                doc_types = {
                    '등기부': 'aceeaea1',
                    '건축물대장': 'aceeair',
                    '감정평가서': 'judgement',
                    '물건명세서': 'mul',
                    '현황조사서': 'status'
                }
                for name, t in doc_types.items():
                    doc_url = f"https://www.my-auction.co.kr/auction/auction_detail_view.php?type={t}&idx={idx}"
                    print(f"Visiting {name} URL: {doc_url}")
                    doc_page = await context.new_page()
                    await doc_page.set_extra_http_headers({
                        "Referer": page.url,
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
                    })
                    await doc_page.goto(doc_url, wait_until="domcontentloaded")
                    await doc_page.wait_for_timeout(2000)
                    
                    doc_html = await doc_page.content()
                    print(f"[{name}] HTML Length: {len(doc_html)}")
                    print(f"[{name}] HTML snippet (first 300 chars):")
                    print(doc_html[:300].strip())
                    
                    # check if page says anything about login or has an iframe
                    doc_soup = BeautifulSoup(doc_html, 'html.parser')
                    if doc_soup.find('iframe'):
                        print(f"[{name}] Found IFRAMES:")
                        for iframe in doc_soup.find_all('iframe'):
                            print(f"  src: {iframe.get('src')}")
                    
                    await doc_page.close()
        else:
            print("No links found on search list!")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
