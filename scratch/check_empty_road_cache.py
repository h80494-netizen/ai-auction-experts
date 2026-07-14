import sqlite3

db_path = "backend/data/map_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all cached grids
cursor.execute("SELECT lat_idx, lng_idx FROM road_cache_grids")
cached_grids = cursor.fetchall()
print(f"Total cached grids in road_cache_grids: {len(cached_grids)}")

empty_count = 0
for lat_idx, lng_idx in cached_grids:
    # Check if there are segments in this grid cell range
    # A segment overlaps with this grid if its bounding box intersects with the cell
    min_lat = lat_idx * 0.01
    max_lat = (lat_idx + 1) * 0.01
    min_lng = lng_idx * 0.01
    max_lng = (lng_idx + 1) * 0.01
    
    cursor.execute('''
        SELECT COUNT(*) FROM road_cache_segments
        WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
          AND highway != '횡단보도'
    ''', (min_lat, max_lat, min_lng, max_lng))
    
    seg_count = cursor.fetchone()[0]
    if seg_count == 0:
        empty_count += 1
        # Print first 20 empty grids to see their locations
        if empty_count <= 20:
            print(f"Empty Grid Cell: lat_idx={lat_idx} ({min_lat:.2f}~{max_lat:.2f}), lng_idx={lng_idx} ({min_lng:.2f}~{max_lng:.2f})")

print(f"Total empty cached grids: {empty_count}")
conn.close()
