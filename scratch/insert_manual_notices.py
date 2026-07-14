import sqlite3
import os
from datetime import datetime

DB_PATH = "c:/Users/llll/Documents/두인경매/바이브코딩/backend/data/map_data.db"
notices = [
    {
        "title": "[서울시 정비사업 고시] 우면한라아파트 재건축 조합설립추진위원회 구성을 위한 주민설명회 개최 안내",
        "source": "서울시 정비사업 정보몽땅",
        "scanned_date": "2026-06-24",
        "keywords": "재개발, 재건축, 고시공고, 서울시, 우면한라",
        "status_label": "고시공고 (서울시)",
        "description": "서울시 정비사업 정보몽땅 고시/공고: 우면한라아파트 재건축 조합설립추진위원회 구성을 위한 주민설명회 개최 안내",
        "url": "https://cleanup.seoul.go.kr/cleanup/bbs/lscr.do",
        "region": "서울특별시",
        "category": "재개발",
        "importance_stars": 5,
        "latitude": 37.4725,
        "longitude": 127.0261
    },
    {
        "title": "[서울시 정비사업 고시] 방배5구역 주택재건축정비사업 관리처분계획 변경인가 고시",
        "source": "서울시 정비사업 정보몽땅",
        "scanned_date": "2026-06-25",
        "keywords": "재개발, 재건축, 고시공고, 서울시, 방배5구역",
        "status_label": "고시공고 (서울시)",
        "description": "서울시 정비사업 정보몽땅 고시/공고: 방배5구역 주택재건축정비사업 관리처분계획 변경인가 고시",
        "url": "https://cleanup.seoul.go.kr/cleanup/bbs/lscr.do",
        "region": "서울특별시",
        "category": "재개발",
        "importance_stars": 4,
        "latitude": 37.4813,
        "longitude": 126.9850
    },
    {
        "title": "[서울시 정비사업 고시] 흑석11재정비촉진구역 주택재개발정비사업 사업시행계획 변경인가 신청에 따른 공람 공고",
        "source": "서울시 정비사업 정보몽땅",
        "scanned_date": "2026-06-26",
        "keywords": "재개발, 재건축, 고시공고, 서울시, 흑석11구역",
        "status_label": "고시공고 (서울시)",
        "description": "서울시 정비사업 정보몽땅 고시/공고: 흑석11재정비촉진구역 주택재개발정비사업 사업시행계획 변경인가 신청에 따른 공람 공고",
        "url": "https://cleanup.seoul.go.kr/cleanup/bbs/lscr.do",
        "region": "서울특별시",
        "category": "재개발",
        "importance_stars": 5,
        "latitude": 37.5056,
        "longitude": 126.9634
    }
]

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
    print("Successfully inserted manual notices into DB.")
except Exception as e:
    print(f"Database error: {e}")
