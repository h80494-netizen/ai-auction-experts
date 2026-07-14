import sqlite3
import time

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

query = """
SELECT * FROM auctions 
WHERE 1=1 
  AND lat BETWEEN 37 AND 38 AND lng BETWEEN 126 AND 127 
  AND (address LIKE '서울%') 
  AND (property_type = '아파트') 
  AND min_bid_rate <= 100 
  AND subway_dist > 0 AND subway_dist <= 500 
LIMIT 1500
"""

cursor.execute(f"EXPLAIN QUERY PLAN {query}")
print("Query Plan:", cursor.fetchall())

start = time.time()
cursor.execute(query)
rows = cursor.fetchall()
end = time.time()
print(f"Fetch count: {len(rows)}, Time taken: {end - start:.4f}s")
