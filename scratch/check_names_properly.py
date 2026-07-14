import sqlite3
import os

db_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT id, name FROM redevelopment_zones LIMIT 30")
for row in cursor.fetchall():
    raw_name = row['name']
    try:
        # Check type of raw_name
        print(f"ID: {row['id']} | type: {type(raw_name)} | repr: {repr(raw_name)}")
    except Exception as e:
        print("Error:", e)

conn.close()
