import sqlite3
import os

DB_PATH = 'backend/data/map_data.db'
if not os.path.exists(DB_PATH):
    print('DB does not exist at:', DB_PATH)
else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating compound indexes for spatial queries optimization...")
    
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_redevelopment_zones_bounds ON redevelopment_zones(max_lat, min_lat, max_lng, min_lng)")
        print("Created index: idx_redevelopment_zones_bounds")
    except Exception as e:
        print("Failed redevelopment index:", e)
        
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_zoning_polygons_bounds ON zoning_polygons(max_lat, min_lat, max_lng, min_lng)")
        print("Created index: idx_zoning_polygons_bounds")
    except Exception as e:
        print("Failed zoning index:", e)
        
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_planning_roads_bounds ON planning_roads(max_lat, min_lat, max_lng, min_lng)")
        print("Created index: idx_planning_roads_bounds")
    except Exception as e:
        print("Failed planning roads index:", e)
        
    conn.commit()
    conn.close()
    print("All compound indexes verified/created successfully!")
