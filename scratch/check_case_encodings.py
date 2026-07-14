import sqlite3

conn = sqlite3.connect('backend/data/map_data.db')
cursor = conn.cursor()

# Get some sample case_nos
cursor.execute("SELECT case_no, address FROM auctions LIMIT 20")
rows = cursor.fetchall()
for case_no, address in rows:
    print(f"Original case_no in DB: {repr(case_no)} | address: {repr(address)}")

conn.close()
