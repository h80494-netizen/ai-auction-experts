import sqlite3
import os

db_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 1. Print tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in map_data.db:", tables)

if "auctions" in tables:
    # 2. Get auctions schema
    cursor.execute("PRAGMA table_info(auctions)")
    columns = [row['name'] for row in cursor.fetchall()]
    print("Auctions columns:", columns)
    
    # 3. Search for case number '6060' or containing '6060'
    cursor.execute("SELECT * FROM auctions WHERE case_no LIKE '%6060%'")
    rows = cursor.fetchall()
    print(f"Found {len(rows)} rows with '6060' in case_no:")
    for row in rows:
        print(dict(row))
        
    # Let's search if there's any case_number matching '2024타경6060' or similar
    cursor.execute("SELECT * FROM auctions LIMIT 5")
    print("First 5 rows in auctions:")
    for row in cursor.fetchall():
        print(dict(row))
else:
    print("auctions table not found!")

conn.close()
