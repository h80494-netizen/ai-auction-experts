import pandas as pd
import sqlite3
import os
import re
import json
import math
import time
import requests
import xml.etree.ElementTree as ET

DB_PATH = 'backend/data/map_data.db'
if not os.path.exists(DB_PATH):
    DB_PATH = 'data/map_data.db'

# OSM API Constants
urls = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "http://localhost:8000/",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
}

def fetch_and_parse_cell(cell_lat, cell_lng):
    c_min_lat = cell_lat * 0.01
    c_max_lat = (cell_lat + 1) * 0.01
    c_min_lng = cell_lng * 0.01
    c_max_lng = (cell_lng + 1) * 0.01

    segments = []
    fetched = False

    # 1. Try Overpass mirrors first
    query = f"""
    [out:json][timeout:15];
    (
      way["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"]({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng});
    );
    out geom;
    """
    for url in urls:
        try:
            print(f"  Fetching via Overpass Mirror: {url}...")
            response = requests.post(url, data={"data": query}, headers=headers, timeout=10.0)
            if response.status_code == 200:
                osm_data = response.json()
                elements = osm_data.get("elements", [])
                
                for el in elements:
                    if el.get("type") == "way" and "geometry" in el:
                        osm_id = el["id"]
                        geom = el["geometry"]
                        coords = [[pt["lon"], pt["lat"]] for pt in geom]
                        if len(coords) < 2:
                            continue
                        
                        tags = el.get("tags", {})
                        name = tags.get("name") or tags.get("name:ko", "소도로")
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
                        segments.append({
                            "osm_id": osm_id,
                            "name": name,
                            "highway": highway,
                            "width": width_val,
                            "min_lat": min(lats),
                            "max_lat": max(lats),
                            "min_lng": min(lngs),
                            "max_lng": max(lngs),
                            "coords_json": json.dumps(coords)
                        })
                fetched = True
                print(f"  Success: Overpass Mirror - {len(segments)} segments parsed.")
                break
            elif response.status_code == 429:
                print(f"  Rate limited (429) by Overpass Mirror {url}. Trying next...")
            else:
                print(f"  Overpass Mirror {url} returned status {response.status_code}.")
        except Exception as e:
            print(f"  Overpass Mirror {url} failed: {e}")

    # 2. Try OSM Main API as fallback if Overpass mirrors failed
    if not fetched:
        try:
            osm_url = f"https://api.openstreetmap.org/api/0.6/map?bbox={c_min_lng},{c_min_lat},{c_max_lng},{c_max_lat}"
            print(f"  Fallback: Fetching via OSM Main API: {osm_url}...")
            response = requests.get(osm_url, headers=headers, timeout=15.0)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                nodes = {}
                for node in root.findall('node'):
                    nodes[node.get('id')] = [float(node.get('lon')), float(node.get('lat'))]
                    
                for w in root.findall('way'):
                    tags = {tag.get('k'): tag.get('v') for tag in w.findall('tag')}
                    highway = tags.get('highway')
                    
                    if highway and any(h_type in highway for h_type in ["residential", "service", "unclassified", "pedestrian", "path", "footway", "living_street"]):
                        osm_id = int(w.get('id'))
                        node_refs = [nd.get('ref') for nd in w.findall('nd')]
                        coords = [nodes[ref] for ref in node_refs if ref in nodes]
                        
                        if len(coords) < 2:
                            continue
                            
                        name = tags.get("name") or tags.get("name:ko") or "소도로"
                        
                        width_val = None
                        width_str = tags.get("width")
                        if width_str:
                            try:
                                match = re.search(r"([0-9.]+)", width_str)
                                if match:
                                    width_val = float(match.group(1))
                            except Exception:
                                pass
                                
                        lats = [pt[1] for pt in coords]
                        lngs = [pt[0] for pt in coords]
                        segments.append({
                            "osm_id": osm_id,
                            "name": name,
                            "highway": highway,
                            "width": width_val,
                            "min_lat": min(lats),
                            "max_lat": max(lats),
                            "min_lng": min(lngs),
                            "max_lng": max(lngs),
                            "coords_json": json.dumps(coords)
                        })
                fetched = True
                print(f"  Success: OSM Main API Fallback - {len(segments)} segments parsed.")
            else:
                print(f"  OSM Main API Fallback returned status {response.status_code}.")
        except Exception as e:
            print(f"  OSM Main API Fallback failed: {e}")

    return fetched, segments

def main(limit=None):
    print(f"Connecting to database: {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get cached cells set
    cursor.execute("SELECT lat_idx, lng_idx FROM road_cache_grids")
    cached_cells = set(cursor.fetchall())

    # Get coordinates of Gyeonggi-do & Incheon auctions
    print("Finding unique uncached grid cells for Gyeonggi-do & Incheon auctions sorted by popularity...")
    cursor.execute('''
        SELECT CAST(lat*100 AS INTEGER) as lat_idx, CAST(lng*100 AS INTEGER) as lng_idx, COUNT(*) as cnt
        FROM auctions
        WHERE (address LIKE '%경기%' OR address LIKE '%경기도%' 
               OR address LIKE '%인천%' OR address LIKE '%인천광역시%')
          AND lat IS NOT NULL AND lng IS NOT NULL
        GROUP BY lat_idx, lng_idx
        ORDER BY cnt DESC
    ''')
    rows = cursor.fetchall()
    
    uncached_cells = []
    for lat_idx, lng_idx, cnt in rows:
        if (lat_idx, lng_idx) not in cached_cells:
            uncached_cells.append((lat_idx, lng_idx))
            
    total_uncached = len(uncached_cells)
    print(f"Found {total_uncached} uncached grid cells.")
    
    if total_uncached == 0:
        print("All Gyeonggi-do & Incheon cells are already cached! Exiting.")
        conn.close()
        return

    if limit is not None:
        uncached_cells = uncached_cells[:limit]
        print(f"Limiting execution to {limit} cells for testing/limit purposes.")

    success_count = 0
    fail_count = 0

    for idx, (lat_idx, lng_idx) in enumerate(uncached_cells):
        print(f"[{idx+1}/{len(uncached_cells)}] Processing cell ({lat_idx}, {lng_idx}) - BBox: [{lat_idx*0.01}, {lng_idx*0.01} to {(lat_idx+1)*0.01}, {(lng_idx+1)*0.01}]")
        
        # Safe-guard: check again in DB if already cached
        cursor.execute("SELECT 1 FROM road_cache_grids WHERE lat_idx=? AND lng_idx=?", (lat_idx, lng_idx))
        if cursor.fetchone():
            print("  Already cached, skipping.")
            continue
            
        fetched, segments = fetch_and_parse_cell(lat_idx, lng_idx)
        
        if fetched:
            # Insert segments sequentially
            inserted = 0
            for seg in segments:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO road_cache_segments 
                        (osm_id, name, highway, width, min_lat, max_lat, min_lng, max_lng, coords_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (seg["osm_id"], seg["name"], seg["highway"], seg["width"], seg["min_lat"], seg["max_lat"], seg["min_lng"], seg["max_lng"], seg["coords_json"]))
                    inserted += 1
                except Exception as db_err:
                    print(f"  DB insert failed for segment {seg['osm_id']}: {db_err}")
            
            # Insert grid cell index
            cursor.execute('INSERT OR REPLACE INTO road_cache_grids (lat_idx, lng_idx) VALUES (?, ?)', (lat_idx, lng_idx))
            conn.commit()
            success_count += 1
            print(f"  Successfully cached cell ({lat_idx}, {lng_idx}) with {inserted} segments.")
        else:
            fail_count += 1
            print(f"  Failed to fetch cell ({lat_idx}, {lng_idx}). Will retry in next run.")
            
        # Politeness sleep to avoid being blocked by OSM (delay 2.0s)
        time.sleep(2.0)

    conn.close()
    print("\nCaching session finished:")
    print(f" - Cells processed: {len(uncached_cells)}")
    print(f" - Successfully cached: {success_count}")
    print(f" - Failed to fetch: {fail_count}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Cache Gyeonggi-do and Incheon road network data in SQLite.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of cells to process.")
    args = parser.parse_args()
    
    main(limit=args.limit)
