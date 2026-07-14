import sqlite3
DB_PATH = r'c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print('Tables:', tables)
if 'deregulation_zones' in tables:
    cursor.execute("SELECT count(*) FROM deregulation_zones")
    print('deregulation_zones count:', cursor.fetchone()[0])
conn.close()
