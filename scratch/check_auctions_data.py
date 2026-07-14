import sqlite3
import os

db_path = 'backend/data/map_data.db'
if not os.path.exists(db_path):
    db_path = 'map_data.db'

print(f"Connecting to {db_path}...")
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('SELECT MIN(lat), MAX(lat), MIN(lng), MAX(lng), COUNT(*) FROM auctions')
print('All auctions lat/lng ranges and count:', c.fetchone())

c.execute('SELECT COUNT(*) FROM auctions WHERE address LIKE "%경기%"')
print('Gyeonggi address count:', c.fetchone()[0])

c.execute('SELECT COUNT(*) FROM auctions WHERE address LIKE "%인천%"')
print('Incheon address count:', c.fetchone()[0])

c.execute('SELECT COUNT(*) FROM auctions WHERE address LIKE "%서울%"')
print('Seoul address count:', c.fetchone()[0])

# Check a sample of Gyeonggi auctions
c.execute('SELECT case_no, address, lat, lng FROM auctions WHERE address LIKE "%경기%" LIMIT 5')
print("\nSample Gyeonggi auctions:")
for row in c.fetchall():
    print(row)

# Check a sample of Incheon auctions
c.execute('SELECT case_no, address, lat, lng FROM auctions WHERE address LIKE "%인천%" LIMIT 5')
print("\nSample Incheon auctions:")
for row in c.fetchall():
    print(row)

conn.close()
