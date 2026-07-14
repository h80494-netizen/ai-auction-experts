import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT DISTINCT highway FROM road_cache_segments")
for row in c.fetchall():
    h = row[0]
    print(f"highway value: {repr(h)}")
    print(f"  Is '도보네트워크'? {h == '도보네트워크'}")
    print(f"  Is '횡단보도'? {h == '횡단보도'}")

conn.close()
