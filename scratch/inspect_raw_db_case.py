import sqlite3

db_path = "backend/data/map_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT case_no FROM auctions LIMIT 5")
for row in cursor.fetchall():
    case_no = row[0]
    print(f"Case No: {repr(case_no)}, type: {type(case_no)}")
    # Print character code points
    code_points = [ord(c) for c in case_no]
    print("Code points:", code_points)

conn.close()
