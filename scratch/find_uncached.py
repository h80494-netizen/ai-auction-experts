import sqlite3
import os

db_path = 'backend/data/map_data.db'
if not os.path.exists(db_path):
    db_path = 'map_data.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT lat_idx, lng_idx FROM road_cache_grids")
cached = set(cursor.fetchall())
print(f"Total cached cells: {len(cached)}")

# Let's check a grid of coordinates in Gyeonggi-do to find one that is NOT cached
# Gyeonggi-do ranges roughly: lat 37.1 to 37.8, lng 126.8 to 127.5
found = False
for lat_idx in range(3710, 3780):
    for lng_idx in range(12680, 12750):
        # lat_idx = int(lat / 0.01) -> lat = lat_idx * 0.01
        cell = (lat_idx, lng_idx)
        if cell not in cached:
            # Let's verify if there is at least one subway, middle school, or auction in this area to make it realistic
            lat = lat_idx * 0.01 + 0.005
            lng = lng_idx * 0.01 + 0.005
            
            # Check if there are any POIs in 5km radius to make it an active Gyeonggi/Incheon area
            cursor.execute("""
                SELECT COUNT(*) FROM subways WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
            """, (lat - 0.05, lat + 0.05, lng - 0.05, lng + 0.05))
            subways_count = cursor.fetchone()[0]
            
            if subways_count > 0:
                print(f"Uncached cell: lat_idx={lat_idx}, lng_idx={lng_idx} -> lat={lat:.4f}, lng={lng:.4f} (nearby subways: {subways_count})")
                found = True
                break
    if found:
        break

conn.close()
