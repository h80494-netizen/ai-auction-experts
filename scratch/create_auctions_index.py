import sqlite3
import os

DB_PATH = 'backend/data/map_data.db'
if not os.path.exists(DB_PATH):
    print('DB does not exist at:', DB_PATH)
else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating spatial index for auctions table...")
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_auctions_lat_lng ON auctions(lat, lng)")
        conn.commit()
        print("SUCCESS: Index idx_auctions_lat_lng created!")
    except Exception as e:
        print("ERROR:", e)
    finally:
        conn.close()
