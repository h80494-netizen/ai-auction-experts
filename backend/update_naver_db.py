import os
import sqlite3
import pandas as pd

def update_naver_db():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "data", "네이버부동산")
    db_path = os.path.join(os.path.dirname(__file__), "data", "map_data.db")
    
    if not os.path.exists(data_dir):
        print(f"Data directory not found: {data_dir}")
        return
        
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute("DROP TABLE IF EXISTS naver_real_estate")
    cursor.execute("""
        CREATE TABLE naver_real_estate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estate_id TEXT UNIQUE,
            address TEXT,
            price TEXT,
            rent TEXT,
            floor TEXT,
            area TEXT,
            deal_type TEXT,
            type_detail TEXT,
            lat REAL,
            lng REAL,
            estate_type TEXT,
            age_info TEXT
        )
    """)
    
    files = {
        "아파트": "네이버부동산_서울_아파트_20260706.xlsx",
        "오피스텔": "네이버부동산_서울_오피스텔_20260707.xlsx",
        "다세대/빌라": "네이버부동산_서울_빌라_20260706.xlsx",
        "단독주택": "네이버부동산_서울_단독_20260708.xlsx",
        "상가": "네이버부동산_서울_상가_20260706.xlsx"
    }
    
    for estate_type, filename in files.items():
        file_path = os.path.join(data_dir, filename)
        if not os.path.exists(file_path):
            print(f"Skipping missing file: {filename}")
            continue
            
        print(f"Loading {filename} ({estate_type})...")
        df = pd.read_excel(file_path)
        
        inserted = 0
        for _, row in df.iterrows():
            try:
                estate_id = str(row.get('매물 번호', ''))
                if not estate_id or estate_id == 'nan':
                    continue
                    
                address = str(row.get('매물위치(주소)', ''))
                price = str(row.get('매매가(보증금)', row.get('금액', '')))
                rent = str(row.get('월세', '0'))
                floor = str(row.get('층수', ''))
                area = str(row.get('공급면적', row.get('전용면적', '')))
                deal_type = str(row.get('거래유형', '매매'))
                type_detail = str(row.get('상세유형', estate_type))
                lat = float(row.get('위도', 0.0))
                lng = float(row.get('경도', 0.0))
                
                desc = str(row.get('보조설명', ''))
                age_info = ''
                if '년' in desc:
                    parts = [p.strip() for p in desc.split(',') if '년' in p]
                    if parts:
                        age_info = parts[0]
                
                # Filter valid coordinates
                if lat == 0.0 or lng == 0.0 or pd.isna(lat) or pd.isna(lng):
                    continue
                    
                cursor.execute("""
                    INSERT INTO naver_real_estate 
                    (estate_id, address, price, rent, floor, area, deal_type, type_detail, lat, lng, estate_type, age_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (estate_id, address, price, rent, floor, area, deal_type, type_detail, lat, lng, estate_type, age_info))
                inserted += 1
            except Exception as e:
                pass
                
        print(f"Inserted {inserted} records for {estate_type}.")
        
    conn.commit()
    conn.close()
    print("Database update complete!")

if __name__ == "__main__":
    update_naver_db()
