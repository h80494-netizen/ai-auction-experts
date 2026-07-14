import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Test LIKE prefix vs LIKE wildcard
for prefix in ['경기', '경기도', '인천', '인천광역시', '서울', '서울특별시']:
    c.execute('SELECT COUNT(*) FROM auctions WHERE address LIKE ?', (prefix + '%',))
    prefix_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM auctions WHERE address LIKE ?', ('%' + prefix + '%',))
    contains_count = c.fetchone()[0]
    print(f"Prefix: '{prefix}%' -> {prefix_count} rows | Contains: '%{prefix}%' -> {contains_count} rows")

print("\nLet's check first 10 characters of some Gyeonggi/Incheon/Seoul addresses:")
c.execute("SELECT address FROM auctions LIMIT 10")
for row in c.fetchall():
    addr = row[0]
    print(f" - {addr[:15]} | bytes hex: {addr[:10].encode('utf-8', errors='replace').hex()}")

conn.close()
