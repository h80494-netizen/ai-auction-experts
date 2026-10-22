import sqlite3
c = sqlite3.connect('backend/data/map_data.db')
print(c.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='auctions'").fetchall())
