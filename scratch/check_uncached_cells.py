import sqlite3
import math

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get unique 0.01 x 0.01 grid cells that contain auctions
c.execute("SELECT lat, lng, address FROM auctions")
cells = set()
regions_count = {"서울": 0, "경기": 0, "인천": 0, "기타": 0}

for lat, lng, addr in c.fetchall():
    lat_idx = int(math.floor(lat / 0.01))
    lng_idx = int(math.floor(lng / 0.01))
    cells.add((lat_idx, lng_idx))
    
    if "서울" in addr:
        regions_count["서울"] += 1
    elif "경기" in addr:
        regions_count["경기"] += 1
    elif "인천" in addr:
        regions_count["인천"] += 1
    else:
        regions_count["기타"] += 1

# Get cached cells
c.execute("SELECT lat_idx, lng_idx FROM road_cache_grids")
cached_cells = set(c.fetchall())

uncached_cells = [cell for cell in cells if cell not in cached_cells]

print(f"Total unique cells with auctions: {len(cells)}")
print(f"Total cached cells: {len(cached_cells)}")
print(f"Uncached cells containing auctions: {len(uncached_cells)}")

# Count uncached cells outside Seoul (Seoul is roughly lat 37.43 to 37.7, lng 126.75 to 127.2)
uncached_outside_seoul = 0
for lat_idx, lng_idx in uncached_cells:
    lat = lat_idx * 0.01
    lng = lng_idx * 0.01
    if not ((37.43 <= lat <= 37.7) and (126.75 <= lng <= 127.2)):
        uncached_outside_seoul += 1

print(f"Uncached cells containing auctions outside Seoul: {uncached_outside_seoul}")

conn.close()
