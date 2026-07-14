import sqlite3
import math
import json

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

lat, lng = 37.380, 126.803
flow_min_lat = lat - 0.0027
flow_max_lat = lat + 0.0027
flow_min_lng = lng - 0.0034
flow_max_lng = lng + 0.0034

center_lat = lat
center_lng = lng

cursor.execute('''
    SELECT name, highway, width, coords_json FROM road_cache_segments
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
      AND highway != '횡단보도'
''', (flow_min_lat, flow_max_lat, flow_min_lng, flow_max_lng))

rows = cursor.fetchall()
print("Initial rows from DB:", len(rows))

width_filtered = 0
coords_err = 0
too_short = 0
distance_filtered = 0
added = 0

for r in rows:
    name, highway, width_val, coords_json = r
    if width_val is not None and width_val > 8.0:
        width_filtered += 1
        continue
    try:
        coords = json.loads(coords_json)
    except Exception:
        coords_err += 1
        continue
    if len(coords) < 2:
        too_short += 1
        continue
    
    for i in range(len(coords) - 1):
        pt1 = coords[i]
        pt2 = coords[i+1]
        
        seg_coords = [pt1, pt2]
        seg_mid_lng = (pt1[0] + pt2[0]) / 2.0
        seg_mid_lat = (pt1[1] + pt2[1]) / 2.0
        
        dy = (seg_mid_lat - center_lat) * 111000.0
        dx = (seg_mid_lng - center_lng) * 88000.0
        dist_from_center_sq = dx*dx + dy*dy
        if dist_from_center_sq > 62500.0:  # 250.0 ** 2
            distance_filtered += 1
            continue
        added += 1

print("width_filtered:", width_filtered)
print("coords_err:", coords_err)
print("too_short:", too_short)
print("distance_filtered:", distance_filtered)
print("added segments:", added)
conn.close()
