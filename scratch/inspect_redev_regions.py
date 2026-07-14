import sqlite3
conn = sqlite3.connect('backend/data/map_data.db')
cursor = conn.cursor()

cursor.execute("SELECT name, min_lat, max_lat, min_lng, max_lng FROM redevelopment_zones LIMIT 10")
print("Sample rows:")
for r in cursor.fetchall():
    print(r[0], "lats:", r[1], r[2], "lngs:", r[3], r[4])

cursor.execute("SELECT COUNT(*) FROM redevelopment_zones WHERE name LIKE '[경기]%'")
print("Gyeonggi count:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM redevelopment_zones WHERE name LIKE '[인천]%'")
print("Incheon count:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM redevelopment_zones WHERE name LIKE '[서울]%'")
print("Seoul count:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM redevelopment_zones")
print("Total count:", cursor.fetchone()[0])

cursor.execute("SELECT MIN(min_lat), MAX(max_lat), MIN(min_lng), MAX(max_lng) FROM redevelopment_zones")
print("Overall bounds:", cursor.fetchone())

conn.close()
