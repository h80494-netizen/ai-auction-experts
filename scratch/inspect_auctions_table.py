import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(auctions)")
columns = cursor.fetchall()
print("=== Columns of auctions table ===")
for col in columns:
    print(col)

cursor.execute("SELECT * FROM auctions LIMIT 1")
row = cursor.fetchone()
print("\n=== Sample row ===")
print(row)

conn.close()
