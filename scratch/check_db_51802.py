import sqlite3
conn = sqlite3.connect('backend/data/map_data.db')
cursor = conn.cursor()
cursor.execute("SELECT case_no, sale_date FROM auctions WHERE case_no LIKE '%51802%'")
print(cursor.fetchall())
conn.close()
