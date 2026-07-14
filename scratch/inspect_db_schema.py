import sqlite3

DB_PATH = 'backend/data/map_data.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

tables = ['redevelopment_zones', 'zoning_polygons', 'planning_roads']

for table in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Table '{table}': {count} rows")
    except Exception as e:
        print(f"Error querying table '{table}': {e}")

conn.close()
