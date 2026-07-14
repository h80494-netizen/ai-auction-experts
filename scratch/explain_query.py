import sqlite3
db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

query = "SELECT * FROM auctions WHERE lat BETWEEN 37 AND 38 AND lng BETWEEN 126 AND 127 LIMIT 1500"
cursor.execute(f"EXPLAIN QUERY PLAN {query}")
print("Query Plan:", cursor.fetchall())

import time
start = time.time()
cursor.execute(query)
rows = cursor.fetchall()
end = time.time()
print(f"Fetch count: {len(rows)}, Time taken: {end - start:.4f}s")
