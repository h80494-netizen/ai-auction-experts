import sqlite3
import os

DB_PATH = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"

if not os.path.exists(DB_PATH):
    print("Database path not found.")
else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM realprice_addr_cache")
    print("Address cache size:", cursor.fetchone()[0])
    conn.close()
