import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM road_cache_segments")
count = cursor.fetchone()[0]
print(f"Total road cache segments: {count}")

# Check coordinates of cached segments
cursor.execute("SELECT min_lat, max_lat, min_lng, max_lng FROM road_cache_segments LIMIT 5")
print("Sample coordinates:")
for r in cursor.fetchall():
    print(f"Lat: {r[0]}~{r[1]}, Lng: {r[2]}~{r[3]}")

# Let's count by region if possible, or coordinate ranges
# Seoul bounds: 37.43 to 37.7 Lat, 126.75 to 127.2 Lng
cursor.execute("SELECT COUNT(*) FROM road_cache_segments WHERE min_lat >= 37.43 AND max_lat <= 37.7 AND min_lng >= 126.75 AND max_lng <= 127.2")
seoul_count = cursor.fetchone()[0]
print(f"Seoul segments: {seoul_count}")
print(f"Non-Seoul segments: {count - seoul_count}")

conn.close()
