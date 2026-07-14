import sqlite3
import math

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get cached cells
cursor.execute("SELECT lat_idx, lng_idx FROM road_cache_grids")
cached_cells = set(cursor.fetchall())

# Find auctions in cached Gyeonggi-do cells
cursor.execute("SELECT case_no, address, lat, lng FROM auctions WHERE address LIKE '%경기%'")
auctions = cursor.fetchall()

print("Auctions in cached Gyeonggi-do cells:")
found = 0
for case_no, address, lat, lng in auctions:
    if lat is None or lng is None:
        continue
    lat_idx = int(math.floor(lat / 0.01))
    lng_idx = int(math.floor(lng / 0.01))
    
    if (lat_idx, lng_idx) in cached_cells:
        print(f"- Case: {case_no} | Address: {address} | Coords: {lat}, {lng} (Cell: {lat_idx}, {lng_idx})")
        found += 1
        if found >= 10:
            break

conn.close()
