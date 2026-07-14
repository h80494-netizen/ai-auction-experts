import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("Distinct highways:")
c.execute("SELECT highway, COUNT(*) FROM road_cache_segments GROUP BY highway")
for h, cnt in c.fetchall():
    print(f"  {repr(h)}: {cnt}")

print("\nSample names for '도보네트워크':")
c.execute("SELECT name, min_lat, min_lng FROM road_cache_segments WHERE highway = '도보네트워크' LIMIT 10")
for name, lat, lng in c.fetchall():
    print(f"  {repr(name)}: ({lat}, {lng})")

conn.close()
