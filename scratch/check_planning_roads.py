import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Count planning roads outside Seoul
c.execute("SELECT COUNT(*) FROM planning_roads WHERE min_lng < 126.75 OR max_lng > 127.2 OR min_lat < 37.43 OR max_lat > 37.7")
count_outside = c.fetchone()[0]

print(f"Total planning roads: {conn.execute('SELECT COUNT(*) FROM planning_roads').fetchone()[0]}")
print(f"Planning roads outside Seoul: {count_outside}")

# Print a few samples of planning roads outside Seoul if they exist
if count_outside > 0:
    c.execute("SELECT id, name, road_class, min_lat, max_lat, min_lng, max_lng FROM planning_roads WHERE min_lng < 126.75 OR max_lng > 127.2 OR min_lat < 37.43 OR max_lat > 37.7 LIMIT 5")
    print("\nSamples outside Seoul:")
    for row in c.fetchall():
        print(row)

conn.close()
