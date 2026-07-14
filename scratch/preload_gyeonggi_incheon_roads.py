import sqlite3
import requests
import json
import time
import re
import math

DB_PATH = 'backend/data/map_data.db'

# Define target areas to pre-cache (latitude/longitude boundaries)
TARGET_AREAS = [
    {
        "name": "Bundang, Gyeonggi-do",
        "min_lat": 37.35,
        "max_lat": 37.42,
        "min_lng": 127.10,
        "max_lng": 127.15
    },
    {
        "name": "Bupyeong, Incheon",
        "min_lat": 37.46,
        "max_lat": 37.52,
        "min_lng": 126.70,
        "max_lng": 126.76
    }
]

urls = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "http://localhost:8000/"
}

def preload():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get currently cached cells
    cursor.execute('SELECT lat_idx, lng_idx FROM road_cache_grids')
    cached_cells = set(cursor.fetchall())
    
    for area in TARGET_AREAS:
        print(f"\n=== Pre-caching roads for {area['name']} ===")
        
        lat_start = int(math.floor(area["min_lat"] / 0.01))
        lat_end = int(math.floor(area["max_lat"] / 0.01))
        lng_start = int(math.floor(area["min_lng"] / 0.01))
        lng_end = int(math.floor(area["max_lng"] / 0.01))
        
        cells_to_fetch = []
        for lat_idx in range(lat_start, lat_end + 1):
            for lng_idx in range(lng_start, lng_end + 1):
                if (lat_idx, lng_idx) not in cached_cells:
                    cells_to_fetch.append((lat_idx, lng_idx))
                    
        print(f"Total cells to fetch: {len(cells_to_fetch)}")
        
        for idx, (cell_lat, cell_lng) in enumerate(cells_to_fetch):
            c_min_lat = cell_lat * 0.01
            c_max_lat = (cell_lat + 1) * 0.01
            c_min_lng = cell_lng * 0.01
            c_max_lng = (cell_lng + 1) * 0.01
            
            print(f"[{idx+1}/{len(cells_to_fetch)}] Fetching cell ({cell_lat}, {cell_lng}) ...")
            
            query = f"""
            [out:json][timeout:10];
            (
              way["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"]({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng});
            );
            out geom;
            """
            
            cell_fetched = False
            for url in urls:
                try:
                    res = requests.post(url, data={"data": query}, headers=headers, timeout=12.0)
                    if res.status_code == 200:
                        osm_data = res.json()
                        elements = osm_data.get("elements", [])
                        
                        segments_inserted = 0
                        for el in elements:
                            if el.get("type") == "way" and "geometry" in el:
                                osm_id = el["id"]
                                geom = el["geometry"]
                                coords = [[pt["lon"], pt["lat"]] for pt in geom]
                                if len(coords) < 2:
                                    continue
                                    
                                tags = el.get("tags", {})
                                name = tags.get("name") or tags.get("name:ko") or "소도로"
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
                                        
                                lats = [pt["lat"] for pt in geom]
                                lngs = [pt["lon"] for pt in geom]
                                min_lat_val = min(lats)
                                max_lat_val = max(lats)
                                min_lng_val = min(lngs)
                                max_lng_val = max(lngs)
                                
                                cursor.execute('''
                                    INSERT OR REPLACE INTO road_cache_segments 
                                    (osm_id, name, highway, width, min_lat, max_lat, min_lng, max_lng, coords_json)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (osm_id, name, highway, width_val, min_lat_val, max_lat_val, min_lng_val, max_lng_val, json.dumps(coords)))
                                segments_inserted += 1
                                
                        cursor.execute('INSERT OR REPLACE INTO road_cache_grids (lat_idx, lng_idx) VALUES (?, ?)', (cell_lat, cell_lng))
                        conn.commit()
                        cell_fetched = True
                        print(f" -> Success! Cached cell ({cell_lat}, {cell_lng}) from {url}. Inserted {segments_inserted} segments.")
                        break
                    else:
                        print(f" -> Mirror {url} returned status code {res.status_code}")
                except Exception as e:
                    print(f" -> Mirror {url} failed: {e}")
                    
            if cell_fetched:
                time.sleep(1.5)  # Rest to avoid Overpass rate limit
            else:
                print(f" -> Failed to fetch cell ({cell_lat}, {cell_lng}) from all mirrors. Skipping for now.")
                time.sleep(2.0)
                
    conn.close()
    print("\nPre-caching complete!")

if __name__ == "__main__":
    preload()
