import sqlite3

db_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, name, propel_cd, min_lat, min_lng FROM redevelopment_zones WHERE name LIKE '[경기]%' LIMIT 10")
print("Gyeonggi zones in DB:")
for row in cursor.fetchall():
    # Print representation to see if there are unicode errors or actual characters
    print(row[0], repr(row[1]), row[2], row[3], row[4])

cursor.execute("SELECT id, name, propel_cd, min_lat, min_lng FROM redevelopment_zones WHERE name LIKE '[인천]%' LIMIT 10")
print("\nIncheon zones in DB:")
for row in cursor.fetchall():
    print(row[0], repr(row[1]), row[2], row[3], row[4])

conn.close()
