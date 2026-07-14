import sqlite3
import math

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT lat, lng FROM auctions WHERE address LIKE '%경기%' OR address LIKE '%인천%'")
rows = c.fetchall()

cells_0_05 = set()
cells_0_1 = set()

for lat, lng in rows:
    lat_idx_0_05 = int(math.floor(lat / 0.05))
    lng_idx_0_05 = int(math.floor(lng / 0.05))
    cells_0_05.add((lat_idx_0_05, lng_idx_0_05))
    
    lat_idx_0_1 = int(math.floor(lat / 0.1))
    lng_idx_0_1 = int(math.floor(lng / 0.1))
    cells_0_1.add((lat_idx_0_1, lng_idx_0_1))

print(f"Total unique 0.05 x 0.05 cells: {len(cells_0_05)}")
print(f"Total unique 0.1 x 0.1 cells: {len(cells_0_1)}")

conn.close()
