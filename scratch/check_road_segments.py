import sqlite3
conn = sqlite3.connect('backend/data/map_data.db')
print("Total road segments:", conn.execute("SELECT COUNT(*) FROM road_segments").fetchone()[0])
print("Road segments outside Seoul:", 
      conn.execute("SELECT COUNT(*) FROM road_segments WHERE min_lng < 126.75 OR max_lng > 127.2 OR min_lat < 37.43 OR max_lat > 37.7").fetchone()[0])
conn.close()
