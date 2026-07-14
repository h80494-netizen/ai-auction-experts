import sqlite3
import traceback
import json

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Try to insert a mock segment
try:
    osm_id = 9999
    name = "테스트도로"
    highway = "residential"
    width_val = 5.0
    min_lat_val = 37.5
    max_lat_val = 37.6
    min_lng_val = 127.0
    max_lng_val = 127.1
    coords = [[127.0, 37.5], [127.1, 37.6]]
    
    cursor.execute('''
        INSERT OR REPLACE INTO road_cache_segments 
        (osm_id, name, highway, width, min_lat, max_lat, min_lng, max_lng, coords_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (osm_id, name, highway, width_val, min_lat_val, max_lat_val, min_lng_val, max_lng_val, json.dumps(coords)))
    conn.commit()
    print("Mock insert succeeded!")
except Exception as e:
    print("Mock insert failed!")
    print(f"Exception message: {e}")
    traceback.print_exc()

conn.close()
