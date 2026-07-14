import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT address FROM auctions LIMIT 100")
print("First 10 sample addresses:")
for r in cursor.fetchall()[:10]:
    print(r[0])

# Group by region using substring or keyword search
cursor.execute("SELECT COUNT(*) FROM auctions WHERE address LIKE '%경기%'")
ggi_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM auctions WHERE address LIKE '%서울%'")
seoul_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM auctions WHERE address LIKE '%인천%'")
incheon_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM auctions")
total_count = cursor.fetchone()[0]

print(f"\nCounts:\nTotal: {total_count}\nSeoul: {seoul_count}\nGyeonggi: {ggi_count}\nIncheon: {incheon_count}\nOther: {total_count - seoul_count - ggi_count - incheon_count}")

conn.close()
