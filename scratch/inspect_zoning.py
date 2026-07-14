import sqlite3
from collections import Counter

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name, COUNT(*) FROM zoning_polygons GROUP BY name")
results = cursor.fetchall()
results.sort(key=lambda x: x[1], reverse=True)

print("Unique names in zoning_polygons:")
for name, count in results:
    print(f"Name: {name}, Count: {count}")

conn.close()
