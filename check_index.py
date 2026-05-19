import sqlite3

db_path = 'c:/Users/llll/Documents/두인경매/바이브코딩/backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='auctions'")
indexes = cursor.fetchall()
print("Auctions Indexes:", indexes)

cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='bus_stops'")
print("Bus Stops Indexes:", cursor.fetchall())

cursor.execute("SELECT COUNT(*) FROM auctions")
print("Total Auctions:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM bus_stops")
print("Total Bus Stops:", cursor.fetchone()[0])
