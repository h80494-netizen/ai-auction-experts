import sqlite3
import os

DB_PATH = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"

if not os.path.exists(DB_PATH):
    print("Database path not found.")
else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT property_type, COUNT(*) FROM realprice_grids GROUP BY property_type")
    rows = cursor.fetchall()
    print("Row counts by property_type in DB:")
    for r in rows:
        print(f"  Property Type: {r[0]} | Count: {r[1]}")
    conn.close()
