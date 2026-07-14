import sqlite3
import pandas as pd
import os
import glob

DB_PATH = os.path.join('backend', 'data', 'map_data.db')
DATA_DIR = os.path.join('data', '네이버부동산')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS naver_real_estate (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estate_type TEXT,
        address TEXT,
        estate_id TEXT,
        type_detail TEXT,
        deal_type TEXT,
        price TEXT,
        rent TEXT,
        floor TEXT,
        area TEXT,
        exclusive_area TEXT,
        description TEXT,
        lat REAL,
        lng REAL
    )
    ''')
    # Clear old data to prevent duplicates on rerun
    cursor.execute('DELETE FROM naver_real_estate')
    conn.commit()
    return conn

def load_data():
    conn = init_db()
    
    files = {
        '아파트': '네이버부동산_서울_아파트_*.xlsx',
        '오피스텔': '네이버부동산_서울_오피스텔_*.xlsx',
        '빌라': '네이버부동산_서울_빌라_*.xlsx',
        '단독주택': '네이버부동산_서울_단독_*.xlsx',
        '상가': '네이버부동산_서울_상가_*.xlsx'
    }
    
    total_inserted = 0
    for estate_type, pattern in files.items():
        matched = glob.glob(os.path.join(DATA_DIR, pattern))
        for file_path in matched:
            print(f"Loading {file_path} as {estate_type}...")
            df = pd.read_excel(file_path)
            
            # Map columns safely
            def get_col(col_name):
                return df[col_name] if col_name in df.columns else None

            # Prepare data
            records = []
            for _, row in df.iterrows():
                lat = row.get('위도')
                lng = row.get('경도')
                if pd.isna(lat) or pd.isna(lng):
                    continue
                
                records.append((
                    estate_type,
                    str(row.get('매물위치(주소)', '')),
                    str(row.get('매물 번호', '')),
                    str(row.get('상세유형', '')),
                    str(row.get('거래유형', '')),
                    str(row.get('매매가(보증금)', '')),
                    str(row.get('월세', '')),
                    str(row.get('층수', '')),
                    str(row.get('공급면적', '')),
                    str(row.get('전용면적', '')),
                    str(row.get('매물설명', '')),
                    float(lat),
                    float(lng)
                ))
            
            cursor = conn.cursor()
            cursor.executemany('''
            INSERT INTO naver_real_estate (
                estate_type, address, estate_id, type_detail, deal_type, price, rent, floor, area, exclusive_area, description, lat, lng
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', records)
            conn.commit()
            total_inserted += len(records)
            print(f"Inserted {len(records)} records from {file_path}")
            
    # Create indices
    conn.cursor().execute('CREATE INDEX IF NOT EXISTS idx_naver_estate_type ON naver_real_estate(estate_type)')
    conn.cursor().execute('CREATE INDEX IF NOT EXISTS idx_naver_lat_lng ON naver_real_estate(lat, lng)')
    conn.commit()
    conn.close()
    
    print(f"Total {total_inserted} records inserted successfully.")

if __name__ == '__main__':
    load_data()
