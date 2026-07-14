import sqlite3
import os

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check counts in road_cache_grids and road_cache_segments
cursor.execute("SELECT COUNT(*) FROM road_cache_grids")
grids_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM road_cache_segments")
segments_count = cursor.fetchone()[0]

print(f"Total road_cache_grids: {grids_count}")
print(f"Total road_cache_segments: {segments_count}")

# Check how many are in Seoul vs outside Seoul
# Seoul bounding box approximate: lat 37.42 ~ 37.70, lng 126.76 ~ 127.19
# We can check lat_idx (lat * 100) and lng_idx (lng * 100)
# e.g. lat_idx between 3742 and 3770, lng_idx between 12676 and 12719

cursor.execute('''
    SELECT COUNT(*) FROM road_cache_grids
    WHERE lat_idx BETWEEN 3742 AND 3770 AND lng_idx BETWEEN 12676 AND 12719
''')
seoul_grids = cursor.fetchone()[0]

print(f"Road cache grids in Seoul BBox: {seoul_grids}")
print(f"Road cache grids outside Seoul BBox (potentially Gyeonggi/Incheon): {grids_count - seoul_grids}")

# Check if there are any auctions in Gyeonggi-do that are NOT cached in road_cache_grids
# For each auction, let's see if its cell (int(lat*100), int(lng*100)) is in road_cache_grids
cursor.execute("SELECT lat, lng, address FROM auctions")
auctions = cursor.fetchall()

uncached_regions = {}
total_gg = 0
uncached_gg = 0

for lat, lng, addr in auctions:
    if lat is None or lng is None:
        continue
    # Check if address contains Gyeonggi
    if "경기" in addr or "경기도" in addr:
        total_gg += 1
        lat_idx = int(lat * 100)
        lng_idx = int(lng * 100)
        cursor.execute("SELECT 1 FROM road_cache_grids WHERE lat_idx=? AND lng_idx=?", (lat_idx, lng_idx))
        if not cursor.fetchone():
            uncached_gg += 1
            city = addr.split()[1] if len(addr.split()) > 1 else "Unknown"
            uncached_regions[city] = uncached_regions.get(city, 0) + 1

print(f"Total Gyeonggi-do auctions: {total_gg}")
print(f"Uncached Gyeonggi-do auctions (cells not in road_cache_grids): {uncached_gg}")
print("Top uncached Gyeonggi-do regions:")
for city, cnt in sorted(uncached_regions.items(), key=lambda x: x[1], reverse=True)[:15]:
    print(f" - {city}: {cnt} auctions")

conn.close()
