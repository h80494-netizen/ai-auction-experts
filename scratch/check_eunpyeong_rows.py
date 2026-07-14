import sqlite3

DB_PATH = "c:/Users/llll/Documents/두인경매/바이브코딩/backend/data/map_data.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Checking redevelopment_zones...")
cursor.execute("SELECT id, name, propel_cd FROM redevelopment_zones WHERE name LIKE '%은평%' OR name LIKE '%진관%' OR name LIKE '%뉴타운%'")
rows = cursor.fetchall()

with open('eunpyeong_rows.txt', 'w', encoding='utf-8') as f:
    for row in rows:
        f.write(f"ID: {row[0]}, Name: {row[1]}, Code: {row[2]}\n")

# If these are exactly what we want to delete, we can delete them.
# The user asked to delete Eunpyeong New Town. We will delete rows containing '은평1지구', '은평2지구', '은평3', '은평뉴타운', etc.

conn.close()
print("Wrote results to eunpyeong_rows.txt")
