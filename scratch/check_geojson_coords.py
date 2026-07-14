import sqlite3
import json

db_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

for table in ['redevelopment_zones', 'zoning_polygons']:
    cursor.execute(f"SELECT id, name, geojson FROM {table} LIMIT 1")
    row = cursor.fetchone()
    print(f"\n--- {table} ---")
    print("ID:", row[0])
    print("Name:", row[1])
    geojson = json.loads(row[2])
    print("Type:", geojson.get('type'))
    if geojson.get('type') == 'Polygon':
        print("Coords count:", len(geojson.get('coordinates', [[]])[0]))
        print("Sample coords:", geojson.get('coordinates', [[]])[0][:5])
    elif geojson.get('type') == 'MultiPolygon':
        print("Coords count:", len(geojson.get('coordinates', [[[]]])[0][0]))
        print("Sample coords:", geojson.get('coordinates', [[[]]])[0][0][:5])

conn.close()
