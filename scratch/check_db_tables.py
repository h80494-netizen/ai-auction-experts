import sqlite3
import os

db_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"
if not os.path.exists(db_path):
    print("Database file does not exist!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get list of tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in database:", tables)

for table in ['redevelopment_zones', 'zoning_polygons']:
    if table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Table '{table}' row count: {count}")
        # Sample one record
        cursor.execute(f"SELECT id, name, min_lat, max_lat, min_lng, max_lng FROM {table} LIMIT 1")
        row = cursor.fetchone()
        print(f"Sample row from '{table}':", row)
    else:
        print(f"Table '{table}' does NOT exist!")

conn.close()
