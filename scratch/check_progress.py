import sqlite3
import math

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get Gyeonggi auctions cells
cursor.execute("SELECT lat, lng FROM auctions WHERE address LIKE '%경기%'")
auctions = cursor.fetchall()

cell_counts = {}
for lat, lng in auctions:
    if lat is None or lng is None:
        continue
    lat_idx = int(math.floor(lat / 0.01))
    lng_idx = int(math.floor(lng / 0.01))
    cell_counts[(lat_idx, lng_idx)] = cell_counts.get((lat_idx, lng_idx), 0) + 1

# Check cached grids
cursor.execute("SELECT lat_idx, lng_idx FROM road_cache_grids")
cached_cells = set(cursor.fetchall())

# Calculate coverage
total_auctions = sum(cell_counts.values())
covered_auctions = sum(count for cell, count in cell_counts.items() if cell in cached_cells)
ggi_cached_cells = [cell for cell in cell_counts if cell in cached_cells]

print(f"Total Gyeonggi auctions: {total_auctions}")
print(f"Currently cached Gyeonggi cells: {len(ggi_cached_cells)} / {len(cell_counts)}")
print(f"Current Gyeonggi auction coverage: {covered_auctions} ({covered_auctions/total_auctions*100:.2f}%)")

cursor.execute("SELECT COUNT(*) FROM road_cache_segments")
total_segments = cursor.fetchone()[0]
print(f"Total road cache segments: {total_segments}")

conn.close()
