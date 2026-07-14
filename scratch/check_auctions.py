import sqlite3
import os

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get coordinate bounds of all auctions
cursor.execute("SELECT MIN(lat), MAX(lat), MIN(lng), MAX(lng) FROM auctions")
min_lat, max_lat, min_lng, max_lng = cursor.fetchone()
print(f"Auctions coordinate bounds: lat({min_lat} ~ {max_lat}), lng({min_lng} ~ {max_lng})")

# Let's count auctions by region
cursor.execute("SELECT SUBSTR(address, 1, 6), COUNT(*) FROM auctions GROUP BY SUBSTR(address, 1, 6) ORDER BY COUNT(*) DESC LIMIT 10")
print("Top regions:")
for r in cursor.fetchall():
    print(f"  {r[0]}: {r[1]}")

# Let's search for auctions near Gangnam [37.4979, 127.0276]
cursor.execute("""
    SELECT case_no, sale_type, property_type, address, lat, lng 
    FROM auctions 
    WHERE lat BETWEEN 37.48 AND 37.52 
      AND lng BETWEEN 127.00 AND 127.05
    LIMIT 5
""")
print("Auctions near Gangnam:")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
