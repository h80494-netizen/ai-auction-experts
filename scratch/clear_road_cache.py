import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Clearing road cache tables...")
cursor.execute("DELETE FROM road_cache_grids")
cursor.execute("DELETE FROM road_cache_segments")
conn.commit()

cursor.execute("SELECT COUNT(*) FROM road_cache_grids")
grids_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM road_cache_segments")
segments_count = cursor.fetchone()[0]

print(f"road_cache_grids: {grids_count} rows")
print(f"road_cache_segments: {segments_count} rows")

conn.close()
print("Done!")
