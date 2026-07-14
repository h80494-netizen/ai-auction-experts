import time
import sqlite3
import math
import json
import random

db_path = 'backend/data/map_data.db'
min_lat, max_lat, min_lng, max_lng = 37.45, 37.54, 126.98, 127.08

center_lat = (min_lat + max_lat) / 2.0
center_lng = (min_lng + max_lng) / 2.0

def fast_dist(lat1, lng1, lat2, lng2):
    dy = (lat1 - lat2) * 111000.0
    dx = (lng1 - lng2) * 88000.0
    return math.sqrt(dx*dx + dy*dy)

# Original query bounds
orig_min_lat, orig_max_lat, orig_min_lng, orig_max_lng = min_lat, max_lat, min_lng, max_lng

# Optimized query bounds (500m radius bounding box around center)
opt_min_lat = center_lat - 0.0045
opt_max_lat = center_lat + 0.0045
opt_min_lng = center_lng - 0.0057
opt_max_lng = center_lng + 0.0057

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Test 1: Original SQL Bounds + Python filtering
start = time.time()
cursor.execute('''
    SELECT name, highway, width, coords_json FROM road_cache_segments
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
      AND highway != '횡단보도'
''', (orig_min_lat, orig_max_lat, orig_min_lng, orig_max_lng))
rows = cursor.fetchall()

parsed_roads_orig = []
for r in rows:
    name, highway, width_val, coords_json = r
    if width_val is not None and width_val > 8.0:
        continue
    try:
        coords = json.loads(coords_json)
    except:
        continue
    if len(coords) < 2:
        continue
    for i in range(len(coords) - 1):
        pt1 = coords[i]
        pt2 = coords[i+1]
        seg_mid_lng = (pt1[0] + pt2[0]) / 2.0
        seg_mid_lat = (pt1[1] + pt2[1]) / 2.0
        dist_from_center = fast_dist(seg_mid_lat, seg_mid_lng, center_lat, center_lng)
        if dist_from_center > 500.0:
            continue
        parsed_roads_orig.append((name, seg_mid_lat, seg_mid_lng))
dur_orig = time.time() - start
print(f"Original logic: {dur_orig:.3f}s, segments found: {len(parsed_roads_orig)}")

# Test 2: Optimized SQL Bounds
start = time.time()
cursor.execute('''
    SELECT name, highway, width, coords_json FROM road_cache_segments
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
      AND highway != '횡단보도'
''', (opt_min_lat, opt_max_lat, opt_min_lng, opt_max_lng))
rows = cursor.fetchall()

parsed_roads_opt = []
for r in rows:
    name, highway, width_val, coords_json = r
    if width_val is not None and width_val > 8.0:
        continue
    try:
        coords = json.loads(coords_json)
    except:
        continue
    if len(coords) < 2:
        continue
    for i in range(len(coords) - 1):
        pt1 = coords[i]
        pt2 = coords[i+1]
        seg_mid_lng = (pt1[0] + pt2[0]) / 2.0
        seg_mid_lat = (pt1[1] + pt2[1]) / 2.0
        dist_from_center = fast_dist(seg_mid_lat, seg_mid_lng, center_lat, center_lng)
        if dist_from_center > 500.0:
            continue
        parsed_roads_opt.append((name, seg_mid_lat, seg_mid_lng))
dur_opt = time.time() - start
print(f"Optimized logic: {dur_opt:.3f}s, segments found: {len(parsed_roads_opt)}")

conn.close()
