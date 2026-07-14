import sqlite3
conn = sqlite3.connect('backend/data/map_data.db')
c = conn.cursor()
c.execute("SELECT line, status, count(*) FROM subway_lines GROUP BY line, status")
for row in c.fetchall():
    print(row)
conn.close()
