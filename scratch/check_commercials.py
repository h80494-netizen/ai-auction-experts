import sqlite3
conn = sqlite3.connect('backend/data/map_data.db')
print("Total commercial areas:", conn.execute("SELECT COUNT(*) FROM commercial_areas").fetchone()[0])
print("Commercial areas in Seoul (approx lat 37.43 to 37.7, lng 126.75 to 127.2):", 
      conn.execute("SELECT COUNT(*) FROM commercial_areas WHERE lat BETWEEN 37.43 AND 37.7 AND lng BETWEEN 126.75 AND 127.2").fetchone()[0])
conn.close()
