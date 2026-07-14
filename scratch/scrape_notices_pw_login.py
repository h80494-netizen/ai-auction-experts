import asyncio
from playwright.async_api import async_playwright
import sqlite3
import os
from datetime import datetime

async def scrape_notices():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navigating to login page...")
        await page.goto("https://cleanup.seoul.go.kr/cleanup/loginMain.do", timeout=60000)
        
        print("Logging in...")
        # Inspecting typical login forms: usually id and password fields
        try:
            await page.fill('input[name="user_id"]', 'h80494')
            await page.fill('input[name="user_password"]', 'spring11!!')
        except:
            try:
                await page.fill('input#user_id', 'h80494')
                await page.fill('input#user_password', 'spring11!!')
            except:
                pass # Will try generic click if inputs are different
        
        # Click login button
        await page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, a, input'));
            const loginBtn = btns.find(b => b.innerText && b.innerText.includes('로그인') || (b.value && b.value.includes('로그인')));
            if(loginBtn) loginBtn.click();
        }""")
        
        # Wait for navigation or a short timeout
        try:
            await page.wait_for_navigation(timeout=5000)
        except:
            await asyncio.sleep(3)
            
        print("Navigating to BBS...")
        await page.goto("https://cleanup.seoul.go.kr/cleanup/bbs/lscr.do", timeout=60000)
        
        print("Extracting notices...")
        # Since .tbl_list might not be the exact class, let's get the main table
        await page.wait_for_selector("table", timeout=10000)
        
        notices = []
        rows = await page.locator("table tbody tr").all()
        for row in rows:
            cols = await row.locator("td").all()
            if len(cols) >= 4: # Number, Title, Author, Date
                try:
                    title_elem = cols[1].locator("a").first
                    if await title_elem.count() > 0:
                        title = await title_elem.inner_text()
                    else:
                        title = await cols[1].inner_text()
                except:
                    title = await cols[1].inner_text()
                    
                title = title.strip()
                author = await cols[2].inner_text()
                date = await cols[3].inner_text()
                
                if title:
                    notices.append({
                        "title": f"[서울시 정비사업 고시] {title}",
                        "source": "서울시 정비사업 정보몽땅",
                        "scanned_date": date.strip() if date else datetime.now().strftime('%Y-%m-%d'),
                        "keywords": "재개발, 재건축, 고시공고, 서울시",
                        "status_label": "고시공고 (서울시)",
                        "description": f"서울시 정비사업 정보몽땅 고시/공고: {title}",
                        "url": "https://cleanup.seoul.go.kr/cleanup/bbs/lscr.do",
                        "region": "서울특별시",
                        "category": "재개발",
                        "importance_stars": 5,
                        "latitude": 37.5665,
                        "longitude": 126.9780
                    })
        
        await browser.close()
        
        print(f"Extracted {len(notices)} notices.")
        for n in notices[:3]:
            print(n["title"], n["scanned_date"])

        if not notices:
            print("Failed to extract notices, maybe login failed or selector is wrong.")
            return

        # Insert them into the DB
        DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'map_data.db'))
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            for notice in notices:
                cursor.execute("SELECT COUNT(*) FROM detected_issues WHERE title = ?", (notice["title"],))
                if cursor.fetchone()[0] == 0:
                    cursor.execute('''
                        INSERT INTO detected_issues (title, source, scanned_date, keywords, status_label, description, url, region, category, importance_stars, latitude, longitude)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (notice["title"], notice["source"], notice["scanned_date"], notice["keywords"], notice["status_label"], notice["description"], notice["url"], notice["region"], notice["category"], notice["importance_stars"], notice["latitude"], notice["longitude"]))
                    
            conn.commit()
            conn.close()
            print("Successfully inserted notices into DB.")
        except Exception as e:
            print(f"Database error: {e}")

if __name__ == "__main__":
    asyncio.run(scrape_notices())
