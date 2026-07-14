import sqlite3
import time

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Gangnam bounds at zoom 13
min_lat, max_lat, min_lng, max_lng = 37.45, 37.54, 126.98, 127.08

print("--- Testing road_cache_segments ---")
# Let's drop existing indexes if any to start clean
cursor.execute("DROP INDEX IF EXISTS idx_road_segments_bounds")
cursor.execute("DROP INDEX IF EXISTS idx_road_segments_lat")
cursor.execute("DROP INDEX IF EXISTS idx_road_segments_lng")
cursor.execute("DROP INDEX IF EXISTS idx_road_segments_min_lat")
cursor.execute("DROP INDEX IF EXISTS idx_road_segments_composite")
conn.commit()

# Measure base time without indexes
start = time.time()
cursor.execute('''
    SELECT name, highway, width, coords_json FROM road_cache_segments
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
      AND highway != '횡단보도'
''', (min_lat, max_lat, min_lng, max_lng))
rows = cursor.fetchall()
dur_base = time.time() - start
print(f"Base time (no index): {dur_base:.3f}s, rows: {len(rows)}")

# Test index 1: single column min_lat
print("Creating index on min_lat...")
cursor.execute("CREATE INDEX idx_road_segments_min_lat ON road_cache_segments(min_lat)")
conn.commit()

start = time.time()
cursor.execute('''
    SELECT name, highway, width, coords_json FROM road_cache_segments
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
      AND highway != '횡단보도'
''', (min_lat, max_lat, min_lng, max_lng))
rows = cursor.fetchall()
dur_idx1 = time.time() - start
print(f"Time with min_lat index: {dur_idx1:.3f}s, rows: {len(rows)}")

# EXPLAIN QUERY PLAN
cursor.execute('''
    EXPLAIN QUERY PLAN
    SELECT name, highway, width, coords_json FROM road_cache_segments
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
      AND highway != '횡단보도'
''', (min_lat, max_lat, min_lng, max_lng))
print("Query Plan:", cursor.fetchall())

# Test index 2: composite index (min_lat, max_lat, min_lng, max_lng)
cursor.execute("DROP INDEX IF EXISTS idx_road_segments_min_lat")
cursor.execute("CREATE INDEX idx_road_segments_composite ON road_cache_segments(min_lat, max_lat, min_lng, max_lng)")
conn.commit()

start = time.time()
cursor.execute('''
    SELECT name, highway, width, coords_json FROM road_cache_segments
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
      AND highway != '횡단보도'
''', (min_lat, max_lat, min_lng, max_lng))
rows = cursor.fetchall()
dur_idx2 = time.time() - start
print(f"Time with composite index: {dur_idx2:.3f}s, rows: {len(rows)}")

cursor.execute('''
    EXPLAIN QUERY PLAN
    SELECT name, highway, width, coords_json FROM road_cache_segments
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
      AND highway != '횡단보도'
''', (min_lat, max_lat, min_lng, max_lng))
print("Query Plan:", cursor.fetchall())

# Let's clean up and keep the best
if dur_idx1 < dur_idx2:
    print("Single index is better. Dropping composite and keeping single.")
    cursor.execute("DROP INDEX IF EXISTS idx_road_segments_composite")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_road_segments_min_lat ON road_cache_segments(min_lat)")
else:
    print("Composite index is better. Keeping composite.")
    cursor.execute("DROP INDEX IF EXISTS idx_road_segments_min_lat")

conn.commit()
conn.close()
