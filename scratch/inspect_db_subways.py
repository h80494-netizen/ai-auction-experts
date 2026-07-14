import sqlite3
import os

db_path = 'backend/data/map_data.db'
if not os.path.exists(db_path):
    print("Database not found!")
    exit(1)

conn = sqlite3.connect(db_path)
c = conn.cursor()

print("--- subways table info ---")
c.execute("PRAGMA table_info(subways)")
for row in c.fetchall():
    print(row)

print("\n--- subway_lines table info ---")
c.execute("PRAGMA table_info(subway_lines)")
for row in c.fetchall():
    print(row)

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("\nAll tables in DB:", [r[0] for r in c.fetchall()])

conn.close()
