import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get column names of auctions table
cursor.execute("PRAGMA table_info(auctions)")
columns = [col[1] for col in cursor.fetchall()]

# Select row 4613
cursor.execute("SELECT * FROM auctions WHERE id = 4613")
row = cursor.fetchone()

print("Row 4613 columns:")
for col_name, value in zip(columns, row):
    try:
        print(f"  {col_name}: {value}")
    except Exception as e:
        print(f"  {col_name}: {repr(value)}")

conn.close()
