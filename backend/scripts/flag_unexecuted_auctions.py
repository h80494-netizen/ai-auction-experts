import sqlite3
import json
import os
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/map_data.db')

def flag_auctions():
    print("Connecting to DB...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(auctions)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'is_unexecuted' not in columns:
        print("Adding is_unexecuted column to auctions table...")
        cursor.execute("ALTER TABLE auctions ADD COLUMN is_unexecuted BOOLEAN DEFAULT 0")
        conn.commit()

    cursor.execute("UPDATE auctions SET is_unexecuted = 0")
    conn.commit()

    current_year = datetime.now().year
    target_year = current_year - 10
    
    print("Loading unexecuted polygons...")
    cursor.execute('''
        SELECT name, geojson FROM unexecuted_facilities 
        WHERE gosi_year <= ? 
        AND (name LIKE '%도로%' OR name LIKE '%공원%' OR name LIKE '%녹지%' OR name LIKE '%광장%')
    ''', (target_year,))
    
    unexecuted_rows = cursor.fetchall()
    
    polygons = []
    for row in unexecuted_rows:
        try:
            geom = shape(json.loads(row[1]))
            if geom.is_valid:
                polygons.append(geom)
        except Exception as e:
            continue

    if not polygons:
        print("No valid polygons found. Exiting.")
        conn.close()
        return

    print(f"Building STRtree for {len(polygons)} polygons...")
    tree = STRtree(polygons)

    print("Checking auctions...")
    cursor.execute("SELECT id, lat, lng FROM auctions WHERE lat IS NOT NULL AND lng IS NOT NULL AND lat != 0 AND lng != 0")
    auctions = cursor.fetchall()
    
    matched_ids = []
    
    for auct in auctions:
        auct_id, lat, lng = auct
        pt = Point(lng, lat)
        
        # Fast bounding box intersection via STRtree
        indices = tree.query(pt)
        
        # Precise intersection
        for idx in indices:
            if polygons[idx].contains(pt):
                matched_ids.append(auct_id)
                break
                
    print(f"Found {len(matched_ids)} auctions within unexecuted zones.")
    
    if matched_ids:
        chunk_size = 500
        for i in range(0, len(matched_ids), chunk_size):
            chunk = matched_ids[i:i+chunk_size]
            placeholders = ','.join(['?'] * len(chunk))
            cursor.execute(f"UPDATE auctions SET is_unexecuted = 1 WHERE id IN ({placeholders})", chunk)
        conn.commit()
        
    print("Update complete.")
    conn.close()

if __name__ == '__main__':
    flag_auctions()
