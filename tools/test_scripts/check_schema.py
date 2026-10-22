import sqlite3
conn = sqlite3.connect('backend/data/map_data.db')
print(conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='auctions'").fetchone()[0])
