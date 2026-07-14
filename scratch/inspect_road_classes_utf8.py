import sqlite3

DB_PATH = 'backend/data/map_data.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("SELECT road_class, COUNT(*) FROM planning_roads GROUP BY road_class")
    rows = cursor.fetchall()
    with open(r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\inspect_road_classes_utf8.txt", "w", encoding="utf-8") as f:
        f.write("Unique road classes in planning_roads:\n")
        for row in rows:
            f.write(f"  {row[0]}: {row[1]} rows\n")
except Exception as e:
    print("Error:", e)

conn.close()
