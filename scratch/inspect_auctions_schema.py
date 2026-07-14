import sqlite3
import os

DB_PATH = 'backend/data/map_data.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(auctions)")
for col in cursor.fetchall():
    print(f'  {col[1]} ({col[2]})')
conn.close()
