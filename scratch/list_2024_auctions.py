import sqlite3

db_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Search for any case_no containing '2024'
cursor.execute("SELECT case_no, address FROM auctions WHERE case_no LIKE '%2024%' LIMIT 100")
rows = cursor.fetchall()
print(f"Total 2024 cases found: {len(rows)}")
for row in rows[:30]:
    print(f"Case No: {row['case_no']} | Address: {row['address'][:60]}")

conn.close()
