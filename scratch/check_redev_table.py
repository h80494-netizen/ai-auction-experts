import sqlite3
import os

db_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check table info
cursor.execute("PRAGMA table_info(redevelopment_zones)")
cols = [dict(row) for row in cursor.fetchall()]
print("Columns in redevelopment_zones:", cols)

# Let's count rows
cursor.execute("SELECT COUNT(*) FROM redevelopment_zones")
count = cursor.fetchone()[0]
print(f"Total rows in redevelopment_zones: {count}")

# Print first 20 rows
cursor.execute("SELECT id, name, propel_cd, geojson FROM redevelopment_zones LIMIT 20")
rows = cursor.fetchall()
for i, r in enumerate(rows):
    d = dict(r)
    # truncate geojson
    if 'geojson' in d and d['geojson']:
        d['geojson'] = d['geojson'][:50] + "..."
    # try decoding if needed or print raw
    print(f"{i}: {d}")

conn.close()
