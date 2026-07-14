import sqlite3
import time

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

lat, lng = 37.380, 126.803
flow_min_lat = lat - 0.0027
flow_max_lat = lat + 0.0027
flow_min_lng = lng - 0.0034
flow_max_lng = lng + 0.0034

start = time.time()
cursor.execute('''
    SELECT name, highway, width, coords_json FROM road_cache_segments
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
      AND highway != '횡단보도'
''', (flow_min_lat, flow_max_lat, flow_min_lng, flow_max_lng))
rows = cursor.fetchall()
duration = time.time() - start
print("Query took:", duration, "seconds")
print("Rows returned:", len(rows))
conn.close()
