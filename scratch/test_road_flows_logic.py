import os
import sys
import math
import sqlite3
import json
import re
import requests

# Add backend directory to sys.path so we can import app
sys.path.append(os.path.abspath('backend'))
from app import get_grid_demographics

print("Imported get_grid_demographics successfully.")

# Bounds (Songpa)
min_lat, max_lat, min_lng, max_lng = 37.510, 37.515, 127.070, 127.075

print("Step 1: Calling get_grid_demographics...")
pad_lat = 0.0045
pad_lng = 0.0057
grid_min_lat = min_lat - pad_lat
grid_max_lat = max_lat + pad_lat
grid_min_lng = min_lng - pad_lng
grid_max_lng = max_lng + pad_lng

top5_grids = []
grid_res = get_grid_demographics(
    min_lat=grid_min_lat,
    max_lat=grid_max_lat,
    min_lng=grid_min_lng,
    max_lng=grid_max_lng,
    type="floating",
    regions="서울,경기,인천"
)
print(f"Status in get_grid_demographics: {grid_res.get('status')}")
grids = grid_res.get("data", [])
print(f"Number of grids loaded: {len(grids)}")

print("Step 2: Processing grid step logic...")
groups = {}
for g in grids:
    r = g.get("region") or "seoul"
    if r not in groups:
        groups[r] = []
    groups[r].append(g)

for r, group_data in groups.items():
    group_data.sort(key=lambda x: x.get("avg_population", 0))
    n = len(group_data)
    if n == 0:
        continue
    for index, item in enumerate(group_data):
        step = int((index / n) * 10) + 1
        step = min(step, 10)
        if step >= 6:
            item["step"] = step
            top5_grids.append(item)
print(f"Number of top5 grids: {len(top5_grids)}")

print("Step 3: Database init...")
db_path = 'backend/data/map_data.db'
if not os.path.exists(db_path):
    db_path = 'map_data.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS road_cache_grids (
        lat_idx INTEGER,
        lng_idx INTEGER,
        PRIMARY KEY (lat_idx, lng_idx)
    )
''')
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
conn.commit()
print("Database schema initialized.")

print("Step 4: Grid cell division...")
lat_start = int(math.floor(min_lat / 0.01))
lat_end = int(math.floor(max_lat / 0.01))
lng_start = int(math.floor(min_lng / 0.01))
lng_end = int(math.floor(max_lng / 0.01))
print(f"Lat range: {lat_start} to {lat_end}, Lng range: {lng_start} to {lng_end}")

# Check cached cells
cursor.execute('SELECT lat_idx, lng_idx FROM road_cache_grids')
cached_cells = set(cursor.fetchall())
print(f"Cached cells in DB: {cached_cells}")

cells_to_fetch = []
for lat_idx in range(lat_start, lat_end + 1):
    for lng_idx in range(lng_start, lng_end + 1):
        if (lat_idx, lng_idx) not in cached_cells:
            cells_to_fetch.append((lat_idx, lng_idx))
print(f"Cells to fetch: {cells_to_fetch}")

print("Step 5: Fetching OSM...")
urls = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.osm.ch/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "http://localhost:8000/",
}

for cell_lat, cell_lng in cells_to_fetch:
    c_min_lat = cell_lat * 0.01
    c_max_lat = (cell_lat + 1) * 0.01
    c_min_lng = cell_lng * 0.01
    c_max_lng = (cell_lng + 1) * 0.01
    print(f"Fetching Overpass for cell ({cell_lat}, {cell_lng}) -> bbox: {c_min_lat},{c_min_lng} to {c_max_lat},{c_max_lng}")
    query = f"""
    [out:json][timeout:2];
    (
      way["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"]({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng});
    );
    out geom;
    """
    cell_fetched = False
    for url in urls:
        print(f"Trying mirror: {url}")
        try:
            response = requests.post(url, data={"data": query}, headers=headers, timeout=5.0)
            print(f"Response status: {response.status_code}")
            if response.status_code == 200:
                osm_data = response.json()
                elements = osm_data.get("elements", [])
                print(f"Found {len(elements)} elements. Storing to DB...")
                
                # DB Storage
                for el in elements:
                    if el.get("type") == "way" and "geometry" in el:
                        osm_id = el["id"]
                        geom = el["geometry"]
                        coords = [[pt["lon"], pt["lat"]] for pt in geom]
                        if len(coords) < 2:
                            continue
                        
                        tags = el.get("tags", {})
                        name = tags.get("name") or tags.get("name:ko", "이면도로")
                        highway = tags.get("highway", "소도로")
                        
                        width_val = None
                        width_str = tags.get("width")
                        if width_str:
                            try:
                                match = re.search(r"([0-9.]+)", width_str)
                                if match:
                                    width_val = float(match.group(1))
                            except Exception:
                                pass
                        
                        lats = [pt[1] for pt in geom]
                        lngs = [pt[0] for pt in geom]
                        min_lat_val = min(lats)
                        max_lat_val = max(lats)
                        min_lng_val = min(lngs)
                        max_lng_val = max(lngs)
                        
                        cursor.execute('''
                            INSERT OR REPLACE INTO road_cache_segments 
                            (osm_id, name, highway, width, min_lat, max_lat, min_lng, max_lng, coords_json)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (osm_id, name, highway, width_val, min_lat_val, max_lat_val, min_lng_val, max_lng_val, json.dumps(coords)))
                
                cursor.execute('INSERT OR REPLACE INTO road_cache_grids (lat_idx, lng_idx) VALUES (?, ?)', (cell_lat, cell_lng))
                conn.commit()
                cell_fetched = True
                print(f"Successfully cached cell ({cell_lat}, {cell_lng})")
                break
        except Exception as e:
            print(f"Mirror {url} failed: {e}")

print("Step 6: Querying cached segments from DB...")
cursor.execute('''
    SELECT name, highway, width, coords_json FROM road_cache_segments
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
''', (min_lat, max_lat, min_lng, max_lng))

rows = cursor.fetchall()
print(f"Found {len(rows)} segments in cached bounds.")

conn.close()
print("Success! Logic testing completed.")
