import sqlite3
db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM road_cache_grids WHERE lat_idx=3737 AND lng_idx=12679")
print("Is Siheung cell (3737, 12679) cached?", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM road_cache_grids WHERE lat_idx=3738 AND lng_idx=12680")
print("Is Siheung cell (3738, 12680) cached?", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM road_cache_segments WHERE min_lat BETWEEN 37.37 AND 37.39 AND min_lng BETWEEN 126.79 AND 126.81")
print("Are there any segments near Siheung?", cursor.fetchone()[0])
conn.close()
