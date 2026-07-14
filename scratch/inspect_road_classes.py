import sqlite3

DB_PATH = 'backend/data/map_data.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("SELECT road_class, COUNT(*) FROM planning_roads GROUP BY road_class")
    rows = cursor.fetchall()
    print("Unique road classes in planning_roads:")
    for row in rows:
        print(f"  {row[0]}: {row[1]} rows")
except Exception as e:
    print("Error:", e)

conn.close()
