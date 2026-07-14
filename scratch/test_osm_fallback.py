import sqlite3
import requests
import xml.etree.ElementTree as ET
import json
import re

db_path = 'backend/data/map_data.db'

# Cell coordinates: Seohyeon station area (3737, 12711) -> lat 37.37 to 37.38, lng 127.11 to 127.12
cell_lat = 3737
cell_lng = 12711

c_min_lat = cell_lat * 0.01
c_max_lat = (cell_lat + 1) * 0.01
c_min_lng = cell_lng * 0.01
c_max_lng = (cell_lng + 1) * 0.01

url = f"https://api.openstreetmap.org/api/0.6/map?bbox={c_min_lng},{c_min_lat},{c_max_lng},{c_max_lat}"
print(f"Fetching from OSM API: {url}")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "http://localhost:8000/",
}

try:
    response = requests.get(url, headers=headers, timeout=20.0)
    print("Status:", response.status_code)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        
        # Parse nodes
        nodes = {}
        for node in root.findall('node'):
            nodes[node.get('id')] = [float(node.get('lon')), float(node.get('lat'))]
            
        print(f"Parsed {len(nodes)} nodes.")
        
        # Parse ways
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        segments_inserted = 0
        for w in root.findall('way'):
            tags = {tag.get('k'): tag.get('v') for tag in w.findall('tag')}
            highway = tags.get('highway')
            
            # Check if it is a relevant highway type
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
                
        # Insert grid cache record
        cursor.execute('INSERT OR REPLACE INTO road_cache_grids (lat_idx, lng_idx) VALUES (?, ?)', (cell_lat, cell_lng))
        conn.commit()
        conn.close()
        
        print(f"Successfully cached cell ({cell_lat}, {cell_lng}). Inserted {segments_inserted} segments.")
    else:
        print("Failed with status:", response.status_code)
except Exception as e:
    print("Failed:", e)
