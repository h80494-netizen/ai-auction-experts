import requests
import json
import sqlite3
import re
import traceback

url = "https://overpass-api.de/api/interpreter"
c_min_lat, c_min_lng, c_max_lat, c_max_lng = 37.50, 127.06, 37.51, 127.07

query = f"""
[out:json][timeout:2];
(
  way["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"]({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng});
);
out geom;
"""

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "http://localhost:8000/",
}

try:
    print("Sending query to Overpass...")
    response = requests.post(url, data={"data": query}, headers=headers, timeout=5.0)
    print("Response status:", response.status_code)
    
    db_path = 'backend/data/map_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    osm_data = response.json()
    elements = osm_data.get("elements", [])
    print(f"Found {len(elements)} elements.")
    
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
            
    cursor.execute('INSERT OR REPLACE INTO road_cache_grids (lat_idx, lng_idx) VALUES (?, ?)', (3750, 12706))
    conn.commit()
    conn.close()
    print("Transaction committed successfully!")
    
except Exception as e:
    print(f"Mirror failed: {e}")
    traceback.print_exc()
