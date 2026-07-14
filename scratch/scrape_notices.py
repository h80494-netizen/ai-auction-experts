import requests
from bs4 import BeautifulSoup
import json
import sqlite3
import os
from datetime import datetime

url = "https://cleanup.seoul.go.kr/cleanup/bbs/lscr.do"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print("Fetching URL:", url)
# We might need post data or specific cookies, but let's try a simple GET first.
response = requests.get(url, headers=headers, verify=False)
soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', class_='tbl_list')
if not table:
    table = soup.find('table')

notices = []
if table:
    rows = table.find('tbody').find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 5:
            # typical columns: number, title, author, date, views
            title_elem = cols[1].find('a')
            if not title_elem:
                title_elem = cols[1]
            title = title_elem.text.strip()
            author = cols[2].text.strip()
            date = cols[3].text.strip()
            
            link = ""
            if title_elem.name == 'a' and title_elem.has_attr('href'):
                link = title_elem['href']
                if link.startswith('/'):
                    link = "https://cleanup.seoul.go.kr" + link
                elif link.startswith('javascript:'):
                    # It might be a JS function, just use the base URL for now
                    link = url
            else:
                link = url
            
            notices.append({
                "title": f"[서울시 정비사업 고시] {title}",
                "source": "서울시 정비사업 정보몽땅",
                "scanned_date": date if date else datetime.now().strftime('%Y-%m-%d'),
                "keywords": "재개발, 재건축, 고시공고, 서울시",
                "status_label": "고시공고 (서울시)",
                "description": f"서울시 정비사업 정보몽땅 고시/공고: {title}",
                "url": link,
                "region": "서울특별시",
                "category": "재개발재건축",
                "importance_stars": 5,
                "latitude": 37.5665,
                "longitude": 126.9780
            })

print(f"Extracted {len(notices)} notices.")
for n in notices[:3]:
    print(n["title"], n["scanned_date"])

# Now insert them into the DB
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'map_data.db'))
print(f"Inserting into {DB_PATH}")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for notice in notices:
        # Check if already exists
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
