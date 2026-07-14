import sqlite3

db_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

with open("scratch/db_out.txt", "w", encoding="utf-8") as f:
    for table in ['redevelopment_zones', 'zoning_polygons']:
        f.write(f"--- Table {table} ---\n")
        cursor.execute(f"SELECT id, name FROM {table} LIMIT 20")
        for row in cursor.fetchall():
            f.write(f"{row[0]}: {repr(row[1])} -> {row[1]}\n")

conn.close()
print("Wrote DB samples to scratch/db_out.txt")
