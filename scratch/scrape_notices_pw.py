import asyncio
from playwright.async_api import async_playwright
import sqlite3
import os
from datetime import datetime

async def scrape_notices():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to URL...")
        await page.goto("https://cleanup.seoul.go.kr/cleanup/bbs/lscr.do", timeout=60000)
        await page.wait_for_selector(".tbl_list", timeout=10000)
        
        notices = []
        rows = await page.locator(".tbl_list tbody tr").all()
        for row in rows:
            cols = await row.locator("td").all()
            if len(cols) >= 5:
                title_elem = cols[1].locator("a").first
                try:
                    # Sometimes the title is directly in the td or inside a span
                    if await title_elem.count() > 0:
                        title = await title_elem.inner_text()
                    else:
                        title = await cols[1].inner_text()
                except:
                    title = await cols[1].inner_text()
                    
                title = title.strip()
                author = await cols[2].inner_text()
                date = await cols[3].inner_text()
                
                notices.append({
                    "title": f"[서울시 정비사업 고시] {title}",
                    "source": "서울시 정비사업 정보몽땅",
                    "scanned_date": date.strip() if date else datetime.now().strftime('%Y-%m-%d'),
                    "keywords": "재개발, 재건축, 고시공고, 서울시",
                    "status_label": "고시공고 (서울시)",
                    "description": f"서울시 정비사업 정보몽땅 고시/공고: {title}",
                    "url": "https://cleanup.seoul.go.kr/cleanup/bbs/lscr.do",
                    "region": "서울특별시",
                    "category": "재개발재건축",
                    "importance_stars": 5,
                    "latitude": 37.5665,
                    "longitude": 126.9780
                })
        
        await browser.close()
        
        print(f"Extracted {len(notices)} notices.")
        for n in notices[:3]:
            print(n["title"], n["scanned_date"])

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
