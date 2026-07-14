import sqlite3
import os
import json
import math

db_path = 'backend/data/map_data.db'
if not os.path.exists(db_path):
    db_path = 'map_data.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Find subways around Jamsil
cursor.execute("SELECT name, lat, lng FROM subways WHERE name LIKE '%잠실%' OR name LIKE '%송파%' LIMIT 5")
subways = cursor.fetchall()
print("Subways:")
for s in subways:
    print(f" - {s[0]}: lat={s[1]}, lng={s[2]}")

if subways:
    s_name, s_lat, s_lng = subways[0]
    # Find cached road segments close to this subway
    # 250m is approx 0.00225 deg lat, 0.0028 deg lng
    d_lat = 0.00225
    d_lng = 0.0028
    cursor.execute("""
        SELECT name, highway, width, coords_json FROM road_cache_segments
        WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
    """, (s_lat - d_lat, s_lat + d_lat, s_lng - d_lng, s_lng + d_lng))
    roads = cursor.fetchall()
    print(f"\nFound {len(roads)} road segments within 250m of {s_name} subway station.")
    for r in roads[:5]:
        print(f" - {r[0]} ({r[1]}): {r[2]}m, coords len={len(json.loads(r[3]))}")

conn.close()
