import sqlite3
import math

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get Gyeonggi auctions
cursor.execute("SELECT lat, lng FROM auctions WHERE address LIKE '%경기%'")
auctions = cursor.fetchall()

boxes = set()
for lat, lng in auctions:
    if lat is None or lng is None:
        continue
    lat_box = int(math.floor(lat / 0.05))
    lng_box = int(math.floor(lng / 0.05))
    boxes.add((lat_box, lng_box))

print(f"Total unique 0.05x0.05 boxes: {len(boxes)}")

# Let's count how many 0.01x0.01 cells are inside these boxes
cells = set()
for lat_box, lng_box in boxes:
    for lat_offset in range(5):
        for lng_offset in range(5):
            lat_idx = lat_box * 5 + lat_offset
            lng_idx = lng_box * 5 + lng_offset
            cells.add((lat_idx, lng_idx))

print(f"Total 0.01x0.01 cells in these boxes: {len(cells)}")

# Check cached status
cursor.execute("SELECT lat_idx, lng_idx FROM road_cache_grids")
cached_cells = set(cursor.fetchall())

uncached_cells = cells - cached_cells
print(f"Uncached 0.01x0.01 cells: {len(uncached_cells)}")

conn.close()
