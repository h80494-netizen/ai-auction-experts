import sqlite3
import requests
import json
import time
import re
import math
import sys
from collections import Counter

DB_PATH = 'backend/data/map_data.db'
urls = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "http://localhost:8000/"
}

def main():
    print("=== [START] Batch Preloading Gyeonggi-do Road Segments ===")
    
    # 1. Connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure tables exist
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS road_cache_grids (
            lat_idx INTEGER,
            lng_idx INTEGER,
            PRIMARY KEY (lat_idx, lng_idx)
        )
    ''')
    conn.commit()
    
    # 2. Get Gyeonggi auctions
    cursor.execute("SELECT lat, lng FROM auctions WHERE address LIKE '%경기%'")
    auctions = cursor.fetchall()
    
    # Count auctions in each cell
    cell_counts = Counter()
    for lat, lng in auctions:
        if lat is None or lng is None:
            continue
        lat_idx = int(math.floor(lat / 0.01))
        lng_idx = int(math.floor(lng / 0.01))
        cell_counts[(lat_idx, lng_idx)] += 1
        
    # Get currently cached cells
    cursor.execute("SELECT lat_idx, lng_idx FROM road_cache_grids")
    cached_cells = set(cursor.fetchall())
    
    # Filter uncached cells and sort by auction count (density)
    uncached_counts = {cell: count for cell, count in cell_counts.items() if cell not in cached_cells}
    sorted_uncached = sorted(uncached_counts.items(), key=lambda x: x[1], reverse=True)
    
    total_auctions = sum(cell_counts.values())
    covered_auctions_cached = sum(count for cell, count in cell_counts.items() if cell in cached_cells)
    
    print(f"Total Gyeonggi auctions: {total_auctions}")
    print(f"Auctions in currently cached cells: {covered_auctions_cached} ({covered_auctions_cached/total_auctions*100:.2f}%)")
    print(f"Total uncached Gyeonggi cells to process: {len(sorted_uncached)}")
    
    if not sorted_uncached:
        print("All Gyeonggi cells are already cached! Nothing to do.")
        conn.close()
        return
        
    # Batch size
    batch_size = 20
    batches = [sorted_uncached[i:i + batch_size] for i in range(0, len(sorted_uncached), batch_size)]
    
    # Optional: limit number of batches to process in a single run to prevent Overpass blocking
    # We can process all or set a limit. Let's process up to 800 cells (40 batches) which covers ~85% of Gyeonggi auctions.
    # We can also process more if it runs fine.
    max_batches = 40 
    print(f"Will process up to {max_batches} batches ({max_batches * batch_size} cells), covering top dense areas.")
    
    running_total = covered_auctions_cached
    for b_idx, batch in enumerate(batches[:max_batches]):
        print(f"\n--- Batch {b_idx+1}/{min(len(batches), max_batches)} ---")
        
        # Build bbox queries
        bbox_queries = []
        batch_cells = []
        batch_auctions_count = 0
        
        for (cell_lat, cell_lng), count in batch:
            batch_cells.append((cell_lat, cell_lng))
            batch_auctions_count += count
            
            c_min_lat = cell_lat * 0.01
            c_max_lat = (cell_lat + 1) * 0.01
            c_min_lng = cell_lng * 0.01
            c_max_lng = (cell_lng + 1) * 0.01
            bbox_queries.append(f'way["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"]({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng});')
            
        # Overpass QL Union Query
        query = f"""
        [out:json][timeout:45];
        (
          {" ".join(bbox_queries)}
        );
        out geom;
        """
        
        success = False
        elements = []
        for url in urls:
            try:
                print(f"Fetching {len(batch)} cells from {url}...")
                t0 = time.time()
                res = requests.post(url, data={"data": query}, headers=headers, timeout=30.0)
                if res.status_code == 200:
                    osm_data = res.json()
                    elements = osm_data.get("elements", [])
                    print(f"  -> Success! Received {len(elements)} elements in {time.time() - t0:.2f}s.")
                    success = True
                    break
                else:
                    print(f"  -> HTTP Error {res.status_code} from {url}")
            except Exception as e:
                print(f"  -> Failed to fetch from {url}: {e}")
                
        if success:
            # Parse and insert segments
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
            
            # Insert cached grids
            for cell_lat, cell_lng in batch_cells:
                cursor.execute('INSERT OR REPLACE INTO road_cache_grids (lat_idx, lng_idx) VALUES (?, ?)', (cell_lat, cell_lng))
                
            conn.commit()
            
            running_total += batch_auctions_count
            coverage_pct = (running_total / total_auctions) * 100
            print(f"  -> Cached {len(batch_cells)} cells. Inserted {segments_inserted} segments.")
            print(f"  -> Cumulative auction coverage: {running_total}/{total_auctions} ({coverage_pct:.2f}%)")
            
            # Sleep to respect rate limits
            time.sleep(2.0)
        else:
            print(f"  -> ERROR: Failed to fetch batch {b_idx+1}. Skipping these cells for now.")
            time.sleep(5.0)
            
    conn.close()
    print("\n=== [FINISHED] Gyeonggi-do Road Preloader Run Complete ===")

if __name__ == "__main__":
    main()
