import pandas as pd
import sqlite3
import requests
import json
import time
import os

DB_PATH = 'backend/data/map_data.db'
CSV_PATH = 'data/road.csv'
API_KEY = '2C1B6EA3-A71D-3294-9749-F878465C245B'

def main():
    print("=== [START] Planning Roads GeoData Import ===")
    
    # 1. Load road.csv
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found")
        return
        
    df = pd.read_csv(CSV_PATH, encoding='cp949')
    print(f"Loaded road.csv with {len(df)} rows.")
    
    # Clean and build lookup dict
    lookup = {}
    for idx, row in df.iterrows():
        sn = row.get('present_sn')
        if not sn or pd.isna(sn):
            continue
        sn = str(sn).strip()
        
        dgm_nm = str(row.get('dgm_nm', ''))
        grad_se = str(row.get('grad_se', ''))
        
        # Categorize
        road_class = '기타'
        if '소로3' in dgm_nm or '소류3' in dgm_nm:
            road_class = '소로3류'
        elif '소로2' in dgm_nm or '소류2' in dgm_nm:
            road_class = '소로2류'
        elif '소로1' in dgm_nm or '소류1' in dgm_nm:
            road_class = '소로1류'
        elif '중로3' in dgm_nm:
            road_class = '중로3류'
        elif '중로2' in dgm_nm:
            road_class = '중로2류'
        elif '중로1' in dgm_nm:
            road_class = '중로1류'
        elif '대로3' in dgm_nm:
            road_class = '대로3류'
        elif '대로2' in dgm_nm:
            road_class = '대로2류'
        elif '대로1' in dgm_nm:
            road_class = '대로1류'
            
        lookup[sn] = {
            'dgm_nm': dgm_nm,
            'grad_se': grad_se,
            'road_class': road_class
        }
        
    print(f"Built lookup dictionary with {len(lookup)} unique present_sn.")
    
    # 2. Connect to database and create table
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS planning_roads")
    cursor.execute('''
        CREATE TABLE planning_roads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            present_sn TEXT UNIQUE,
            name TEXT,
            road_class TEXT,
            min_lat REAL,
            max_lat REAL,
            min_lng REAL,
            max_lng REAL,
            geojson TEXT
        )
    ''')
    cursor.execute("CREATE INDEX idx_planning_roads_min_lat ON planning_roads(min_lat)")
    cursor.execute("CREATE INDEX idx_planning_roads_max_lat ON planning_roads(max_lat)")
    cursor.execute("CREATE INDEX idx_planning_roads_min_lng ON planning_roads(min_lng)")
    cursor.execute("CREATE INDEX idx_planning_roads_max_lng ON planning_roads(max_lng)")
    cursor.execute("CREATE INDEX idx_planning_roads_class ON planning_roads(road_class)")
    conn.commit()
    
    # 3. Fetch from VWorld WFS / REST API
    # BOX covering almost entirety of South Korea: BOX(125,34,130,39)
    # Total features: 253,395. We will fetch in pages of 1,000.
    page = 1
    size = 1000
    matched_count = 0
    total_pages = 255
    
    print("Fetching spatial data from VWorld API in batches of 1000...")
    while page <= total_pages:
        url = f"http://api.vworld.kr/req/data?key={API_KEY}&domain=http://localhost&service=data&version=2.0&request=GetFeature&format=json&size={size}&page={page}&data=lt_c_upisuq151&geomFilter=BOX(125,34,130,39)"
        
        try:
            t0 = time.time()
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                print(f"Error fetching page {page}: HTTP {r.status_code}")
                time.sleep(1)
                continue
                
            res = r.json()
            status = res.get('response', {}).get('status')
            if status != 'OK':
                print(f"API Error at page {page}: {status}")
                break
                
            features = res.get('response', {}).get('result', {}).get('featureCollection', {}).get('features', [])
            if not features:
                print(f"No features returned at page {page}")
                break
                
            insert_rows = []
            for f in features:
                properties = f.get('properties', {})
                sn = properties.get('present_sn')
                if not sn:
                    continue
                sn = str(sn).strip()
                
                if sn in lookup:
                    info = lookup[sn]
                    # We got a match!
                    geom = f.get('geometry')
                    if not geom:
                        continue
                        
                    # Calculate bbox bounds
                    # geom coordinates can be MultiPolygon or Polygon
                    # Let's flatten coordinates to find bounds
                    def get_coords_bounds(coords):
                        flat_coords = []
                        def flatten(lst):
                            for item in lst:
                                if isinstance(item, list):
                                    if len(item) == 2 and isinstance(item[0], (int, float)):
                                        flat_coords.append(item)
                                    else:
                                        flatten(item)
                        flatten(coords)
                        if not flat_coords:
                            return None
                        lngs = [c[0] for c in flat_coords]
                        lats = [c[1] for c in flat_coords]
                        return min(lats), max(lats), min(lngs), max(lngs)
                        
                    bounds = get_coords_bounds(geom.get('coordinates', []))
                    if not bounds:
                        continue
                        
                    min_lat, max_lat, min_lng, max_lng = bounds
                    geojson_str = json.dumps(geom)
                    
                    insert_rows.append((sn, info['dgm_nm'], info['road_class'], min_lat, max_lat, min_lng, max_lng, geojson_str))
                    
            if insert_rows:
                cursor.executemany('''
                    INSERT OR REPLACE INTO planning_roads (present_sn, name, road_class, min_lat, max_lat, min_lng, max_lng, geojson)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', insert_rows)
                conn.commit()
                matched_count += len(insert_rows)
                
            dt = time.time() - t0
            print(f"Processed page {page}/{total_pages} (time: {dt:.2f}s). Matched so far: {matched_count}/{len(lookup)}")
            
            # If we matched all, we can break early!
            if matched_count >= len(lookup):
                print("All features matched! Breaking early.")
                break
                
            page += 1
            # Avoid rate limit
            time.sleep(0.05)
            
        except Exception as e:
            print(f"Exception at page {page}: {e}")
            time.sleep(2)
            
    conn.close()
    print(f"\n=== [FINISHED] Imported {matched_count} roads into database. ===")

if __name__ == '__main__':
    main()
