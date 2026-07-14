import sqlite3
import time

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

min_lat, max_lat, min_lng, max_lng = 37.0, 38.0, 126.0, 128.0

queries = [
    ("auctions", '''
        SELECT * FROM auctions
        WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
        LIMIT 1500
    ''', (min_lat, max_lat, min_lng, max_lng)),
    
    ("pois - bus_stops", '''
        SELECT name, lat, lng FROM bus_stops 
        WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ? LIMIT 500
    ''', (min_lat, max_lat, min_lng, max_lng)),
    
    ("district_units", '''
        SELECT id, name, geojson FROM district_units
        WHERE max_lat >= ? AND min_lat <= ? 
          AND max_lng >= ? AND min_lng <= ?
        LIMIT 500
    ''', (min_lat, max_lat, min_lng, max_lng)),
    
    ("road_cache_segments", '''
        SELECT name, highway, width, coords_json FROM road_cache_segments
        WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
          AND highway != '횡단보도'
    ''', (min_lat, max_lat, min_lng, max_lng))
]

print("Direct DB Query Timing:")
for name, sql, params in queries:
    start = time.time()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    dur = time.time() - start
    print(f" - {name}: {dur:.3f}s, Rows returned: {len(rows)}")

conn.close()
