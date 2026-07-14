import os
import sys
import sqlite3
import zipfile
import tempfile
import shutil
import json
import traceback
import pandas as pd

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'map_data.db')

# zip 파일 찾기
ZIP_PATH = os.path.join(DATA_DIR, '특별계획구역.zip')
if not os.path.exists(ZIP_PATH):
    # 크기로 찾기 (441121 바이트)
    for f in os.listdir(DATA_DIR):
        if f.endswith('.zip'):
            p = os.path.join(DATA_DIR, f)
            if os.path.getsize(p) == 441121:
                ZIP_PATH = p
                break

if not os.path.exists(ZIP_PATH):
    print("특별계획구역.zip (또는 441121바이트 zip 파일)을 찾을 수 없습니다.")
    sys.exit(1)

print(f"Processing ZIP file: {ZIP_PATH}")

try:
    import geopandas as gpd
except ImportError:
    print("geopandas is required. Please install it using: pip install geopandas")
    sys.exit(1)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deregulation_zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            details TEXT,
            min_lat REAL,
            max_lat REAL,
            min_lng REAL,
            max_lng REAL,
            geojson TEXT
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_deregulation_zones_lat ON deregulation_zones (min_lat, max_lat)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_deregulation_zones_lng ON deregulation_zones (min_lng, max_lng)')
    
    # 기존 특별계획구역 데이터 지우기 (초기화)
    cursor.execute("DELETE FROM deregulation_zones WHERE type='특별계획구역'")
    conn.commit()
    return conn

def main():
    conn = init_db()
    cursor = conn.cursor()

    temp_dir = tempfile.mkdtemp()
    try:
        # 1. 압축 해제 (인코딩 문제 방지를 위해 일반 이름으로 압축해제 시도)
        with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
            zf.extractall(temp_dir)
            
        # 2. .shp 파일 찾기
        shp_path = None
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith('.shp'):
                    shp_path = os.path.join(root, file)
                    break
            if shp_path:
                break
                
        if not shp_path:
            print("No shapefile found in the zip archive.")
            return

        print(f"Found shapefile: {shp_path}")
        
        # 3. GeoPandas로 읽기 (euc-kr 인코딩 시도)
        try:
            gdf = gpd.read_file(shp_path, encoding='euc-kr')
        except Exception as e:
            print("Failed with euc-kr, trying cp949")
            gdf = gpd.read_file(shp_path, encoding='cp949')
            
        print(f"Total features: {len(gdf)}")
        print(f"Columns: {gdf.columns.tolist()}")

        # 4. 좌표계 변환 (EPSG:5174 or EPSG:5186 등 -> EPSG:4326)
        # 만약 CRS가 설정되어 있지 않다면 국토지리정보원 표준(5174 등)으로 추정하고 변환
        if gdf.crs is None:
            # 보편적으로 UPIS는 5186, 5174 둘 중 하나를 씀. 우선 5174로 시도
            print("CRS not found. Assuming EPSG:5174 (Bessel)")
            gdf.set_crs(epsg=5174, inplace=True)
            
        print(f"Original CRS: {gdf.crs}")
        
        # WGS84(4326)으로 변환
        gdf = gdf.to_crs(epsg=4326)
        print(f"Converted CRS: {gdf.crs}")
        
        # 5. DB에 삽입
        count = 0
        for idx, row in gdf.iterrows():
            geom = row.geometry
            if geom is None or geom.is_empty:
                continue
                
            bounds = geom.bounds # (minx, miny, maxx, maxy)
            if not bounds:
                continue
            
            min_lng, min_lat, max_lng, max_lat = bounds
            
            # GeoJSON 변환
            geojson_str = json.dumps(geom.__geo_interface__)
            
            # 속성 추출 (이름 찾기)
            # DGM_NM 또는 MNM 등의 열이 이름일 가능성이 높음
            name = "특별계획구역"
            details_dict = {}
            for col in gdf.columns:
                if col != 'geometry':
                    val = row[col]
                    if pd.notna(val):
                        details_dict[col] = str(val)
                        if 'NM' in col.upper() or '이름' in col or '명칭' in col:
                            if name == "특별계획구역":
                                name = str(val)
            
            details_str = json.dumps(details_dict, ensure_ascii=False)
            
            cursor.execute('''
                INSERT INTO deregulation_zones (name, type, details, min_lat, max_lat, min_lng, max_lng, geojson)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, '특별계획구역', details_str, min_lat, max_lat, min_lng, max_lng, geojson_str))
            
            count += 1

        conn.commit()
        print(f"Successfully inserted {count} special planning zones into DB.")
        
    except Exception as e:
        print(f"Error processing data: {e}")
        traceback.print_exc()
    finally:
        shutil.rmtree(temp_dir)
        conn.close()

if __name__ == "__main__":
    main()
