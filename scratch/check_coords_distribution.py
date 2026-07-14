import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 1. Total count of Gyeonggi address contains
c.execute('SELECT COUNT(*) FROM auctions WHERE address LIKE "%경기%"')
total_gg_addr = c.fetchone()[0]

# 2. Count of Gyeonggi address within lat/lng range (Gyeonggi/Incheon roughly 37.0 to 38.2, 126.3 to 127.6)
c.execute('SELECT COUNT(*) FROM auctions WHERE address LIKE "%경기%" AND (lat BETWEEN 37.0 AND 38.2) AND (lng BETWEEN 126.3 AND 127.6)')
gg_in_range = c.fetchone()[0]

# 3. Gyeonggi auctions outside this range
c.execute('SELECT COUNT(*) FROM auctions WHERE address LIKE "%경기%" AND NOT ((lat BETWEEN 37.0 AND 38.2) AND (lng BETWEEN 126.3 AND 127.6))')
gg_out_range = c.fetchone()[0]

print(f"Total Gyeonggi address: {total_gg_addr}")
print(f"Gyeonggi in lat/lng range: {gg_in_range}")
print(f"Gyeonggi out of lat/lng range: {gg_out_range}")

# 4. Check min/max lat/lng specifically for Gyeonggi
c.execute('SELECT MIN(lat), MAX(lat), MIN(lng), MAX(lng) FROM auctions WHERE address LIKE "%경기%"')
print(f"Gyeonggi coordinates range: {c.fetchone()}")

# 5. Let's count Gyeonggi auctions in Bundang:
# Bundang is roughly lat: 37.34 ~ 37.42, lng: 127.09 ~ 127.16
c.execute('SELECT COUNT(*) FROM auctions WHERE address LIKE "%경기%" AND (lat BETWEEN 37.34 AND 37.42) AND (lng BETWEEN 127.09 AND 127.16)')
print(f"Gyeonggi auctions in Bundang: {c.fetchone()[0]}")

# Let's see if there are any Gyeonggi auctions in Bundang, print a few if exists
c.execute('SELECT case_no, address, lat, lng FROM auctions WHERE address LIKE "%경기%" AND (lat BETWEEN 37.34 AND 37.42) AND (lng BETWEEN 127.09 AND 127.16) LIMIT 5')
print("\nSample Bundang auctions:")
for row in c.fetchall():
    print(row)

conn.close()
