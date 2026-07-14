import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT lat, lng, address FROM auctions WHERE address LIKE '%서초동 1373%' LIMIT 5")
rows = c.fetchall()
if rows:
    for lat, lng, addr in rows:
        print(f"Address: {addr} | Lat: {lat}, Lng: {lng}")
else:
    # Look for any Seocho-dong
    print("Not found for 서초동 1373, finding any 서초동...")
    c.execute("SELECT lat, lng, address FROM auctions WHERE address LIKE '%서초동%' LIMIT 5")
    for lat, lng, addr in c.fetchall():
        print(f"Address: {addr} | Lat: {lat}, Lng: {lng}")

conn.close()
