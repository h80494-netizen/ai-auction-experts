import sqlite3
import os

DB_PATH = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"

if not os.path.exists(DB_PATH):
    print("Database path not found.")
else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print("Tables in map_data.db:")
    for t in tables:
        cursor.execute(f"PRAGMA table_info({t})")
        cols = [c[1] for c in cursor.fetchall()]
        print(f"  Table: {t} | Columns: {cols}")
    conn.close()
