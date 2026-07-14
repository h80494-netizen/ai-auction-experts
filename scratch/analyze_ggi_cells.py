import sqlite3
import math

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all cached cells
cursor.execute("SELECT lat_idx, lng_idx FROM road_cache_grids")
cached_cells = set(cursor.fetchall())
print(f"Total cached cells in DB: {len(cached_cells)}")

# Get all Gyeonggi-do auctions and their corresponding grid cells
cursor.execute("SELECT lat, lng, address FROM auctions WHERE address LIKE '%경기%'")
auctions = cursor.fetchall()
print(f"Total Gyeonggi auctions: {len(auctions)}")

ggi_cells = set()
for lat, lng, addr in auctions:
    if lat is None or lng is None:
        continue
    lat_idx = int(math.floor(lat / 0.01))
    lng_idx = int(math.floor(lng / 0.01))
    ggi_cells.add((lat_idx, lng_idx))

print(f"Total unique cells for Gyeonggi auctions: {len(ggi_cells)}")

uncached_ggi_cells = ggi_cells - cached_cells
print(f"Total uncached cells for Gyeonggi auctions: {len(uncached_ggi_cells)}")

# Print a few examples of uncached cells
print("Sample uncached Gyeonggi cells:")
for cell in list(uncached_ggi_cells)[:10]:
    # Find one auction address in this cell
    cursor.execute("SELECT address, lat, lng FROM auctions WHERE address LIKE '%경기%' AND CAST(lat/0.01 AS INT) = ? AND CAST(lng/0.01 AS INT) = ? LIMIT 1", cell)
    res = cursor.fetchone()
    if res:
        print(f"Cell {cell}: {res[0]} (lat: {res[1]}, lng: {res[2]})")
    else:
        print(f"Cell {cell}")

conn.close()
