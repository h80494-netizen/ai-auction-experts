import sqlite3
import os

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('SELECT DISTINCT highway FROM road_cache_segments')
highways = [r[0] for r in c.fetchall()]

print("Raw unique highway values:")
for h in highways:
    # Print the string and its hex representation of UTF-8 encoded bytes
    hex_repr = h.encode('utf-8', errors='replace').hex()
    print(f"String: {repr(h)} | Hex: {hex_repr}")

conn.close()
