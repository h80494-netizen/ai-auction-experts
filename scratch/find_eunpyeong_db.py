import sqlite3

DB_PATH = "c:/Users/llll/Documents/두인경매/바이브코딩/backend/data/map_data.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Checking redevelopment_zones...")
try:
    cursor.execute("SELECT id, name, propel_cd FROM redevelopment_zones WHERE name LIKE '%은평%' OR name LIKE '%진관%' OR name LIKE '%뉴타운%'")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
except Exception as e:
    print("Error:", e)

print("\nChecking district_units...")
try:
    cursor.execute("SELECT id, name FROM district_units WHERE name LIKE '%은평%' OR name LIKE '%진관%' OR name LIKE '%뉴타운%'")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
except Exception as e:
    print("Error:", e)

conn.close()
