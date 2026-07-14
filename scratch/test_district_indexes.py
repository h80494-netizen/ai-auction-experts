import sqlite3
import time

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Gangnam bounds at zoom 13
min_lat, max_lat, min_lng, max_lng = 37.45, 37.54, 126.98, 127.08

print("--- Testing district_units ---")
# Drop existing index to start clean
cursor.execute("DROP INDEX IF EXISTS idx_district_units_bounds")
cursor.execute("DROP INDEX IF EXISTS idx_district_units_min_lat")
cursor.execute("DROP INDEX IF EXISTS idx_district_units_composite")
conn.commit()

# Measure base time without indexes
start = time.time()
cursor.execute('''
    SELECT id, name, geojson FROM district_units
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
    LIMIT 500
''', (min_lat, max_lat, min_lng, max_lng))
rows = cursor.fetchall()
dur_base = time.time() - start
print(f"Base time (no index): {dur_base:.3f}s, rows: {len(rows)}")

# Test index 1: single column min_lat
print("Creating index on min_lat...")
cursor.execute("CREATE INDEX idx_district_units_min_lat ON district_units(min_lat)")
conn.commit()

start = time.time()
cursor.execute('''
    SELECT id, name, geojson FROM district_units
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
    LIMIT 500
''', (min_lat, max_lat, min_lng, max_lng))
rows = cursor.fetchall()
dur_idx1 = time.time() - start
print(f"Time with min_lat index: {dur_idx1:.3f}s, rows: {len(rows)}")

cursor.execute('''
    EXPLAIN QUERY PLAN
    SELECT id, name, geojson FROM district_units
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
    LIMIT 500
''', (min_lat, max_lat, min_lng, max_lng))
print("Query Plan:", cursor.fetchall())

# Test index 2: composite index
cursor.execute("DROP INDEX IF EXISTS idx_district_units_min_lat")
cursor.execute("CREATE INDEX idx_district_units_composite ON district_units(min_lat, max_lat, min_lng, max_lng)")
conn.commit()

start = time.time()
cursor.execute('''
    SELECT id, name, geojson FROM district_units
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
    LIMIT 500
''', (min_lat, max_lat, min_lng, max_lng))
rows = cursor.fetchall()
dur_idx2 = time.time() - start
print(f"Time with composite index: {dur_idx2:.3f}s, rows: {len(rows)}")

cursor.execute('''
    EXPLAIN QUERY PLAN
    SELECT id, name, geojson FROM district_units
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
    LIMIT 500
''', (min_lat, max_lat, min_lng, max_lng))
print("Query Plan:", cursor.fetchall())

conn.close()
