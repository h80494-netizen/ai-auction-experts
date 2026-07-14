import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT name FROM zoning_polygons")
names = [r[0] for r in cursor.fetchall() if r[0]]

with open('scratch/zoning_names.txt', 'w', encoding='utf-8') as f:
    for n in sorted(names):
        f.write(f"{n}\n")

print(f"Total unique zoning names: {len(names)}. Written to scratch/zoning_names.txt")
conn.close()
