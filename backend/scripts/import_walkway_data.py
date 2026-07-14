import pandas as pd
import sqlite3
import os
import re
import json

DB_PATH = 'backend/data/map_data.db'
if not os.path.exists(DB_PATH):
    DB_PATH = 'data/map_data.db'

def parse_wkt_linestring(wkt_str):
    if not isinstance(wkt_str, str):
        return None
    try:
        # Extract numbers between parentheses
        coords_str = wkt_str.replace("LINESTRING", "").replace("(", "").replace(")", "").strip()
        pts = coords_str.split(",")
        coords = []
        for pt in pts:
            xy = pt.strip().split()
            if len(xy) == 2:
                coords.append([float(xy[0]), float(xy[1])]) # [lng, lat]
        if len(coords) >= 2:
            return coords
    except Exception:
        pass
    return None

def import_walkways():
    print(f"Connecting to DB: {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure tables and index exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS road_cache_segments (
            osm_id INTEGER PRIMARY KEY,
            name TEXT,
            highway TEXT,
            width REAL,
            min_lat REAL,
            max_lat REAL,
            min_lng REAL,
            max_lng REAL,
            coords_json TEXT
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_road_cache_bounds ON road_cache_segments(max_lat, min_lat, max_lng, min_lng)')
    
    # We clear the existing procedurally generated or old cache segments so we have ONLY real walkway data in Seoul
    print("Clearing old road cache segments to avoid mixed straight radial lines...")
    cursor.execute("DELETE FROM road_cache_segments")
    conn.commit()

    # 1. Import 서울시 자치구별 도보 네트워크 공간정보.csv
    walk_path = 'data/서울시 자치구별 도보 네트워크 공간정보.csv'
    if os.path.exists(walk_path):
        print(f"Processing walkway network from {walk_path}...")
        # Since the file is 112MB, we read in chunks to prevent memory blowup
        chunk_count = 0
        total_inserted = 0
        
        for chunk in pd.read_csv(walk_path, encoding='cp949', chunksize=50000):
            chunk_count += 1
            print(f"  Reading chunk {chunk_count}...")
            
            # Filter rows where 노드링크 유형 is 'LINK'
            links = chunk[chunk['노드링크 유형'] == 'LINK']
            if links.empty:
                continue
                
            # Filter for pedestrian-walkable (first digit is 1): LINK_CODE is between 1000 and 1199
            # In binary or string code: 1000 to 1111 (represented as decimal 1000 to 1199)
            links = links[(links['링크 유형 코드'] >= 1000) & (links['링크 유형 코드'] < 1200)]
            if links.empty:
                continue
                
            batch = []
            for _, row in links.iterrows():
                link_id = int(row['링크 ID'])
                wkt = row['링크 WKT']
                coords = parse_wkt_linestring(wkt)
                if not coords:
                    continue
                    
                sgg_name = str(row.get('시군구명', ''))
                dong_name = str(row.get('읍면동명', ''))
                name = f"{sgg_name} {dong_name} 도보길".strip()
                highway = "도보네트워크"
                width = 4.0 # default walkway width
                
                lats = [pt[1] for pt in coords]
                lngs = [pt[0] for pt in coords]
                min_lat = min(lats)
                max_lat = max(lats)
                min_lng = min(lngs)
                max_lng = max(lngs)
                
                batch.append((link_id, name, highway, width, min_lat, max_lat, min_lng, max_lng, json.dumps(coords)))
            
            if batch:
                cursor.executemany('''
                    INSERT OR REPLACE INTO road_cache_segments 
                    (osm_id, name, highway, width, min_lat, max_lat, min_lng, max_lng, coords_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', batch)
                total_inserted += len(batch)
                conn.commit()
                
        print(f"Successfully loaded {total_inserted} walkway segments from {walk_path}!")

    # 2. Import 서울시 대로변 횡단보도 위치정보.csv
    cross_path = 'data/서울시 대로변 횡단보도 위치정보.csv'
    if os.path.exists(cross_path):
        print(f"Processing crosswalk network from {cross_path}...")
        df_cross = pd.read_csv(cross_path, encoding='cp949')
        
        links = df_cross[df_cross['노드링크 유형'] == 'LINK']
        links = links[(links['링크 유형 코드'] >= 1000) & (links['링크 유형 코드'] < 1200)]
        
        batch = []
        for _, row in links.iterrows():
            link_id = int(row['링크 ID']) + 900000000 # Add offset to avoid osm_id collision with walkway segments
            wkt = row['링크 WKT']
            coords = parse_wkt_linestring(wkt)
            if not coords:
                continue
                
            sgg_name = str(row.get('시군구명', ''))
            dong_name = str(row.get('읍면동명', ''))
            name = f"{sgg_name} {dong_name} 횡단보도".strip()
            highway = "횡단보도"
            width = 6.0
            
            lats = [pt[1] for pt in coords]
            lngs = [pt[0] for pt in coords]
            min_lat = min(lats)
            max_lat = max(lats)
            min_lng = min(lngs)
            max_lng = max(lngs)
            
            batch.append((link_id, name, highway, width, min_lat, max_lat, min_lng, max_lng, json.dumps(coords)))
            
        if batch:
            cursor.executemany('''
                INSERT OR REPLACE INTO road_cache_segments 
                (osm_id, name, highway, width, min_lat, max_lat, min_lng, max_lng, coords_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', batch)
            conn.commit()
            print(f"Successfully loaded {len(batch)} crosswalk segments from {cross_path}!")

    # Also, we flag the grids in road_cache_grids as CACHED so the server doesn't hit Overpass API for these areas!
    # Specifically, since this walkway data spans Seoul, we can seed the grid cache for Seoul coordinates.
    # Seoul bounding box is roughly 37.4 to 37.7 Lat, 126.7 to 127.2 Lng.
    # We can pre-cache all these grid cells!
    print("Pre-seeding road cache grids for Seoul region to disable live Overpass queries...")
    lat_start = int(math.floor(37.4 / 0.01))
    lat_end = int(math.floor(37.7 / 0.01))
    lng_start = int(math.floor(126.7 / 0.01))
    lng_end = int(math.floor(127.2 / 0.01))
    
    grid_batch = []
    for lat_idx in range(lat_start, lat_end + 1):
        for lng_idx in range(lng_start, lng_end + 1):
            grid_batch.append((lat_idx, lng_idx))
            
    cursor.executemany('INSERT OR REPLACE INTO road_cache_grids (lat_idx, lng_idx) VALUES (?, ?)', grid_batch)
    conn.commit()
    print("Seoul road grids successfully pre-cached!")

    conn.close()
    print("Walkway migration complete.")

if __name__ == "__main__":
    import math
    import time
    start = time.time()
    import_walkways()
    print(f"Finished walkway import in {time.time() - start:.2f} seconds.")
