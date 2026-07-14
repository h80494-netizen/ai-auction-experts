import sqlite3

db_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM redevelopment_zones WHERE name LIKE '[인천]%'")
incheon_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM redevelopment_zones WHERE name LIKE '[경기]%'")
gyeonggi_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM redevelopment_zones WHERE name NOT LIKE '[인천]%' AND name NOT LIKE '[경기]%'")
seoul_count = cursor.fetchone()[0]

print(f"Seoul count: {seoul_count}")
print(f"Incheon count: {incheon_count}")
print(f"Gyeonggi count: {gyeonggi_count}")

if gyeonggi_count > 0:
    cursor.execute("SELECT id, name, propel_cd, min_lat, max_lat, min_lng, max_lng FROM redevelopment_zones WHERE name LIKE '[경기]%' LIMIT 5")
    print("\nSample Gyeonggi rows:")
    for row in cursor.fetchall():
        print(row)

if incheon_count > 0:
    cursor.execute("SELECT id, name, propel_cd, min_lat, max_lat, min_lng, max_lng FROM redevelopment_zones WHERE name LIKE '[인천]%' LIMIT 5")
    print("\nSample Incheon rows:")
    for row in cursor.fetchall():
        print(row)

conn.close()
