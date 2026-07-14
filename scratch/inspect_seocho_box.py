import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("""
    SELECT highway, COUNT(*) 
    FROM road_cache_segments 
    WHERE max_lat >= 37.490 AND min_lat <= 37.500 AND max_lng >= 127.025 AND min_lng <= 127.035 
    GROUP BY highway
""")
print("Highway type counts in Seocho box:")
for h, cnt in c.fetchall():
    print(f"  {repr(h)}: {cnt}")

conn.close()
