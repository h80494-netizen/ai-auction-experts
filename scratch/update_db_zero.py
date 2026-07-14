import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Replace '0 #' with '대항력 없음 #' and '0.0 #' with '대항력 없음 #'
cursor.execute("UPDATE auctions SET special_notes = REPLACE(special_notes, '0 #', '대항력 없음 #') WHERE special_notes LIKE '0 #%'")
cursor.execute("UPDATE auctions SET special_notes = REPLACE(special_notes, '0.0 #', '대항력 없음 #') WHERE special_notes LIKE '0.0 #%'")
cursor.execute("UPDATE auctions SET special_notes = '대항력 없음' WHERE special_notes = '0' OR special_notes = '0.0'")

conn.commit()

cursor.execute("SELECT COUNT(*) FROM auctions WHERE special_notes LIKE '%대항력 없음%'")
print('Updated count:', cursor.fetchone()[0])
conn.close()
