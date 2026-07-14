import sqlite3
import os
import json

backend_dir = os.path.abspath("backend")
DB_PATH = os.path.abspath(os.path.join(backend_dir, 'data', 'map_data.db'))

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

min_lat, max_lat, min_lng, max_lng = 37.61110382089148, 37.63313016525288, 127.05379486083986, 127.11207389831544

cursor.execute('''
    SELECT name, coords_json FROM crosswalk_segments
    WHERE max_lat >= ? AND min_lat <= ? 
      AND max_lng >= ? AND min_lng <= ?
''', (min_lat, max_lat, min_lng, max_lng))

rows = cursor.fetchall()
print("Raw rows fetched:", len(rows))

for i, r in enumerate(rows[:5]):
    name, coords_json = r['name'], r['coords_json']
    print(f"\nRow {i+1} - name: {name}")
    print(f"coords_json content: {repr(coords_json)} (type: {type(coords_json)})")
    try:
        coords = json.loads(coords_json)
        print("Parse SUCCESS, coords length:", len(coords))
    except Exception as pe:
        print("Parse FAILED:", pe)

conn.close()
