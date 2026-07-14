import sqlite3
import json

def test_api():
    conn = sqlite3.connect('backend/data/map_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    min_lat, max_lat = 37.48, 37.49
    min_lng, max_lng = 126.99, 127.00
    
    cursor.execute('''
        SELECT name, coords_json FROM crosswalk_segments
        WHERE max_lat >= ? AND min_lat <= ? 
          AND max_lng >= ? AND min_lng <= ?
        LIMIT 10
    ''', (min_lat, max_lat, min_lng, max_lng))
    
    rows = cursor.fetchall()
    print(f"Found {len(rows)} crosswalks in bounding box:")
    for r in rows:
        print(r['name'], r['coords_json'])
    
    conn.close()

if __name__ == '__main__':
    test_api()
