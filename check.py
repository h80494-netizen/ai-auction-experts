import sqlite3
c = sqlite3.connect('backend/data/map_data.db')
schema = c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='auctions'").fetchone()[0]
print(schema)
