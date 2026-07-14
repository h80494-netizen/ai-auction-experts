import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get coordinate bounds of population_grids
cursor.execute("SELECT MIN(lat), MAX(lat), MIN(lng), MAX(lng) FROM population_grids")
min_lat, max_lat, min_lng, max_lng = cursor.fetchone()
print(f"Population Grids coordinates range: Lat {min_lat} ~ {max_lat}, Lng {min_lng} ~ {max_lng}")

# Check if there are any rows in Gyeonggi-do
# Seoul is roughly lat 37.42 ~ 37.70, lng 126.76 ~ 127.19
cursor.execute('''
    SELECT COUNT(*) FROM population_grids
    WHERE lat NOT BETWEEN 37.42 AND 37.70 OR lng NOT BETWEEN 126.76 AND 127.19
''')
outside_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM population_grids")
total_count = cursor.fetchone()[0]

print(f"Total population grids: {total_count}")
print(f"Population grids outside Seoul: {outside_count}")

# Check first 5 grids outside Seoul
cursor.execute('''
    SELECT lat, lng, avg_population FROM population_grids
    WHERE lat NOT BETWEEN 37.42 AND 37.70 OR lng NOT BETWEEN 126.76 AND 127.19
    LIMIT 5
''')
print("Sample grids outside Seoul:", cursor.fetchall())

conn.close()
