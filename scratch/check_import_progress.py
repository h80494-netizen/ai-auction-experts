import sqlite3
import os

db_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"

if not os.path.exists(db_path):
    print("Database not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get total count of Incheon redevelopment zones
cursor.execute("SELECT COUNT(*) FROM redevelopment_zones WHERE name LIKE '[인천]%'")
incheon_count = cursor.fetchone()[0]

# Get total count of Gyeonggi redevelopment zones
cursor.execute("SELECT COUNT(*) FROM redevelopment_zones WHERE name LIKE '[경기]%'")
gyeonggi_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM redevelopment_zones")
total_count = cursor.fetchone()[0]

print(f"Total Incheon zones imported: {incheon_count} (out of 141)")
print(f"Total Gyeonggi zones imported so far: {gyeonggi_count} (out of 493)")
print(f"Total zones in DB: {total_count}")

# Print first 5 imported Gyeonggi zones to verify details if any exist
cursor.execute("SELECT id, name, propel_cd, min_lat, max_lat, min_lng, max_lng FROM redevelopment_zones WHERE name LIKE '[경기]%' LIMIT 5")
rows = cursor.fetchall()
for r in rows:
    print(r)

conn.close()
