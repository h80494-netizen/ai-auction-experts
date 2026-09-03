import os
import zipfile
import sqlite3
import pandas as pd
import time

def build_small_business_db():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    zip_path = os.path.join(base_dir, "data", "소상공인", "소상공인시장진흥공단_상가(상권)정보_20251231.zip")
    db_path = os.path.join(base_dir, "backend", "data", "small_business.db")
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS small_business")
    cursor.execute("""
        CREATE TABLE small_business (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bizes_id TEXT,
            name TEXT,
            branch TEXT,
            cat_large_code TEXT,
            cat_large_name TEXT,
            cat_medium_code TEXT,
            cat_medium_name TEXT,
            cat_small_code TEXT,
            cat_small_name TEXT,
            inds_code TEXT,
            inds_name TEXT,
            sido_code TEXT,
            sido_name TEXT,
            sigungu_code TEXT,
            sigungu_name TEXT,
            dong_code TEXT,
            dong_name TEXT,
            road_addr TEXT,
            lot_addr TEXT,
            building_name TEXT,
            floor_info TEXT,
            ho_info TEXT,
            lng REAL,
            lat REAL
        )
    """)
    
    if not os.path.exists(zip_path):
        print(f"Zip file not found: {zip_path}")
        return
        
    print(f"Opening zip file: {zip_path}")
    start_time = time.time()
    
    # Priority targets: Seoul, Gyeonggi, Incheon (or all if feasible)
    # The user specifically requested Gyeonggi and nearby auction properties
    target_keywords = ["서울", "경기", "인천", "강원", "충남", "충북", "세종", "대전", "대구", "부산", "울산", "경북", "경남", "전북", "전남", "광주", "제주"]
    
    total_inserted = 0
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        entries = z.infolist()
        for info in entries:
            raw_name = info.filename
            try:
                name = raw_name.encode('cp437').decode('cp949')
            except:
                name = raw_name
                
            if not name.endswith('.csv'):
                continue
                
            print(f"Processing {name} (size: {info.file_size:,} bytes)...")
            
            with z.open(info.filename) as f:
                # Read in chunks for memory efficiency
                chunk_size = 50000
                chunks = pd.read_csv(f, chunksize=chunk_size, encoding='utf-8', low_memory=False)
                
                file_inserted = 0
                for chunk in chunks:
                    # Filter valid lat / lng
                    chunk = chunk.dropna(subset=['위도', '경도'])
                    
                    rows = []
                    for _, row in chunk.iterrows():
                        try:
                            lat = float(row.get('위도', 0))
                            lng = float(row.get('경도', 0))
                            if lat == 0 or lng == 0 or pd.isna(lat) or pd.isna(lng):
                                continue
                                
                            b_id = str(row.get('상가업소번호', ''))
                            b_name = str(row.get('상호명', ''))
                            branch = str(row.get('지점명', '')) if pd.notnull(row.get('지점명')) else ''
                            c_large_cd = str(row.get('상권업종대분류코드', ''))
                            c_large = str(row.get('상권업종대분류명', ''))
                            c_med_cd = str(row.get('상권업종중분류코드', ''))
                            c_med = str(row.get('상권업종중분류명', ''))
                            c_sml_cd = str(row.get('상권업종소분류코드', ''))
                            c_sml = str(row.get('상권업종소분류명', ''))
                            inds_cd = str(row.get('표준산업분류코드', ''))
                            inds_nm = str(row.get('표준산업분류명', ''))
                            sido_cd = str(row.get('시도코드', ''))
                            sido_nm = str(row.get('시도명', ''))
                            sigungu_cd = str(row.get('시군구코드', ''))
                            sigungu_nm = str(row.get('시군구명', ''))
                            dong_cd = str(row.get('법정동코드', ''))
                            dong_nm = str(row.get('법정동명', ''))
                            road_addr = str(row.get('도로명주소', '')) if pd.notnull(row.get('도로명주소')) else ''
                            lot_addr = str(row.get('지번주소', '')) if pd.notnull(row.get('지번주소')) else ''
                            bldg = str(row.get('건물명', '')) if pd.notnull(row.get('건물명')) else ''
                            floor = str(row.get('층정보', '')) if pd.notnull(row.get('층정보')) else ''
                            ho = str(row.get('호정보', '')) if pd.notnull(row.get('호정보')) else ''
                            
                            rows.append((
                                b_id, b_name, branch, c_large_cd, c_large, c_med_cd, c_med,
                                c_sml_cd, c_sml, inds_cd, inds_nm, sido_cd, sido_nm, sigungu_cd,
                                sigungu_nm, dong_cd, dong_nm, road_addr, lot_addr, bldg, floor,
                                ho, lng, lat
                            ))
                        except Exception:
                            pass
                            
                    if rows:
                        cursor.executemany("""
                            INSERT INTO small_business (
                                bizes_id, name, branch, cat_large_code, cat_large_name,
                                cat_medium_code, cat_medium_name, cat_small_code, cat_small_name,
                                inds_code, inds_name, sido_code, sido_name, sigungu_code,
                                sigungu_name, dong_code, dong_name, road_addr, lot_addr,
                                building_name, floor_info, ho_info, lng, lat
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, rows)
                        file_inserted += len(rows)
                        total_inserted += len(rows)
                        
                conn.commit()
                print(f"  Inserted {file_inserted:,} stores from {name}. Total so far: {total_inserted:,}")
                
    print("Creating indexes on lat, lng, dong_name, cat_large_name...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sb_lat_lng ON small_business(lat, lng)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sb_dong ON small_business(dong_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sb_cat_large ON small_business(cat_large_name)")
    conn.commit()
    conn.close()
    
    elapsed = time.time() - start_time
    print(f"Successfully built small_business.db with {total_inserted:,} stores in {elapsed:.2f}s!")

if __name__ == "__main__":
    build_small_business_db()
