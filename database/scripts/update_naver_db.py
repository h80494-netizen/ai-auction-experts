import os
import sqlite3
import pandas as pd
import time

def update_naver_db():
    start_time = time.time()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data", "네이버부동산")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "map_data.db")
    
    if not os.path.exists(data_dir):
        print(f"Data directory not found: {data_dir}")
        return
        
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    import sys
    drop_table = '--drop' in sys.argv
    if drop_table:
        print("Dropping existing naver_real_estate table...")
        cursor.execute("DROP TABLE IF EXISTS naver_real_estate")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS naver_real_estate (
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
            region TEXT,
            age_info TEXT
        )
    """)
    conn.commit()
    
    filter_keywords = [arg for arg in sys.argv[1:] if not arg.startswith('--')]
    
    # Dynamically scan all excel and csv files in data_dir
    files_info = []
    for f in os.listdir(data_dir):
        if not (f.endswith('.xlsx') or f.endswith('.xlsm') or f.endswith('.csv')) or f.startswith('~$'):
            continue
            
        if filter_keywords and not any(kw in f for kw in filter_keywords):
            continue
            
        # Determine region
        if "인천" in f:
            region = "인천"
        elif "서울" in f:
            region = "서울"
        elif "경기" in f:
            region = "경기"
        else:
            region = "전국"
            
        # Determine estate_type
        if "아파트" in f:
            estate_type = "아파트"
        elif "빌라" in f or "연립" in f or "다세대" in f:
            estate_type = "다세대/빌라"
        elif "오피스텔" in f:
            estate_type = "오피스텔"
        elif "단독" in f or "다가구" in f:
            estate_type = "단독주택"
        elif "상가" in f:
            estate_type = "상가"
        else:
            estate_type = "기타"
            
        files_info.append({
            "file": f,
            "estate_type": estate_type,
            "region": region
        })
        
    print(f"Discovered {len(files_info)} file(s) in {data_dir}:")
    for item in files_info:
        print(f"  - {item['file']} => Region: {item['region']}, Type: {item['estate_type']}")
    print("-" * 60)
    
    total_inserted = 0
    
    for item in files_info:
        filename = item["file"]
        estate_type = item["estate_type"]
        region = item["region"]
        file_path = os.path.join(data_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"Skipping missing file: {filename}")
            continue
            
        print(f"Loading {filename} ({estate_type}, {region})...", flush=True)
        t_load = time.time()
        if filename.endswith('.csv'):
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
            except Exception:
                try:
                    df = pd.read_csv(file_path, encoding='cp949')
                except Exception:
                    df = pd.read_csv(file_path, encoding='euc-kr')
        else:
            try:
                df = pd.read_excel(file_path, engine="calamine")
            except Exception as e:
                print(f"  [WARN] Calamine failed for {filename}: {e}. Trying openpyxl...", flush=True)
                df = pd.read_excel(file_path, engine="openpyxl")
            
        print(f"  Loaded {len(df)} rows in {time.time()-t_load:.2f}s. Preparing records...", flush=True)
        
        records = []
        for _, row in df.iterrows():
            try:
                estate_id = str(row.get('매물 번호', '')).strip()
                if not estate_id or estate_id.lower() == 'nan' or estate_id == 'None':
                    continue
                    
                address = str(row.get('매물위치(주소)', '')).strip()
                price = str(row.get('매매가(보증금)', row.get('금액', ''))).strip()
                rent = str(row.get('월세', '0')).strip()
                floor = str(row.get('층수', '')).strip()
                area = str(row.get('공급면적', row.get('전용면적', ''))).strip()
                deal_type = str(row.get('거래유형', '매매')).strip()
                type_detail = str(row.get('상세유형', estate_type)).strip()
                
                try:
                    lat = float(row.get('위도', 0.0))
                    lng = float(row.get('경도', 0.0))
                except (ValueError, TypeError):
                    continue
                    
                if lat == 0.0 or lng == 0.0 or pd.isna(lat) or pd.isna(lng):
                    continue
                    
                desc = str(row.get('보조설명', ''))
                age_info = ''
                if '년' in desc:
                    parts = [p.strip() for p in desc.split(',') if '년' in p]
                    if parts:
                        age_info = parts[0]

                # Determine specific region per row
                row_region = region
                if row_region == "전국":
                    rcode = str(row.get('지역코드', '')).strip()
                    if rcode.startswith('11'):
                        row_region = "서울"
                    elif rcode.startswith('28'):
                        row_region = "인천"
                    elif rcode.startswith('41'):
                        row_region = "경기"
                    elif '서울' in address:
                        row_region = "서울"
                    elif '인천' in address:
                        row_region = "인천"
                    elif '경기' in address:
                        row_region = "경기"
                        
                records.append((
                    estate_id, address, price, rent, floor, area,
                    deal_type, type_detail, lat, lng, estate_type, row_region, age_info
                ))
            except Exception:
                pass
                
        # Batch insert with INSERT OR IGNORE to handle duplicate estate_ids
        insert_sql = """
            INSERT OR IGNORE INTO naver_real_estate 
            (estate_id, address, price, rent, floor, area, deal_type, type_detail, lat, lng, estate_type, region, age_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        batch_size = 5000
        inserted_for_file = 0
        for i in range(0, len(records), batch_size):
            chunk = records[i:i + batch_size]
            cursor.executemany(insert_sql, chunk)
            conn.commit()
            inserted_for_file += len(chunk)
            
        total_inserted += inserted_for_file
        print(f"  Processed {inserted_for_file} records for {filename}.", flush=True)
        
    print("Creating indexes...", flush=True)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_naver_estate_id ON naver_real_estate(estate_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_naver_type_coords ON naver_real_estate(estate_type, lat, lng)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_naver_region_type_coords ON naver_real_estate(region, estate_type, lat, lng)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_naver_coords ON naver_real_estate(lat, lng)")
    conn.commit()
    
    # Print statistics
    cursor.execute("SELECT region, estate_type, count(*) FROM naver_real_estate GROUP BY region, estate_type")
    stats = cursor.fetchall()
    print("\n=== Data Statistics in DB ===", flush=True)
    for s in stats:
        print(f"Region: {s[0]}, Type: {s[1]}, Count: {s[2]:,}건", flush=True)
        
    cursor.execute("SELECT count(*) FROM naver_real_estate")
    total_count = cursor.fetchone()[0]
    print(f"Total Unique Records: {total_count:,}건", flush=True)
    
    conn.close()
    print(f"Database update complete in {time.time()-start_time:.2f}s!", flush=True)

if __name__ == "__main__":
    update_naver_db()
