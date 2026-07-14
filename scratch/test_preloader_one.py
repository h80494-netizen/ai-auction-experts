import sqlite3
import requests
import json
import re

DB_PATH = 'backend/data/map_data.db'
# A cell in Bundang (lat index 3738, lng index 12712)
cell_lat = 3738
cell_lng = 12712

c_min_lat = cell_lat * 0.01
c_max_lat = (cell_lat + 1) * 0.01
c_min_lng = cell_lng * 0.01
c_max_lng = (cell_lng + 1) * 0.01

query = f"""
[out:json][timeout:15];
(
  way["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"]({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng});
);
out geom;
"""

urls = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "http://localhost:8000/"
}

print(f"Querying cell ({cell_lat}, {cell_lng}) ...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

for url in urls:
    print(f"Trying URL: {url} ...")
    try:
        res = requests.post(url, data={"data": query}, headers=headers, timeout=15.0)
        print("Status code:", res.status_code)
        if res.status_code == 200:
            osm_data = res.json()
            elements = osm_data.get("elements", [])
            print(f"Successfully retrieved {len(elements)} elements.")
            
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
            print(f"Successfully inserted {segments_inserted} segments into road_cache_segments.")
            break
        else:
            print("Error text:", res.text[:200])
    except Exception as e:
        import traceback
        traceback.print_exc()

conn.close()
print("Done!")
