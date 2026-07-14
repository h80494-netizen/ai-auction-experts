import sqlite3
db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='road_cache_segments'")
print("Table Schema:")
print(cursor.fetchone()[0])

cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='road_cache_segments'")
print("\nIndexes on road_cache_segments:")
for row in cursor.fetchall():
    print(row)
conn.close()
