import sqlite3
import os

DB_PATH = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"

if not os.path.exists(DB_PATH):
    print("Database path not found.")
else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT property_type FROM realprice_grids")
    rows = cursor.fetchall()
    print("Distinct property_type in DB (repr):")
    for r in rows:
        val = r[0]
        print(f"  Value: {repr(val)} | Encoded utf-8: {val.encode('utf-8') if isinstance(val, str) else val}")
    conn.close()
