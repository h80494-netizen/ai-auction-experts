import sqlite3

db_path = 'c:/Users/llll/Documents/두인경매/바이브코딩/backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Creating indexes on auctions table...")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_auctions_lat_lng ON auctions(lat, lng)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_auctions_sale_type ON auctions(sale_type)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_auctions_min_rate ON auctions(min_bid_rate)")

conn.commit()
print("Indexes created successfully!")
conn.close()
