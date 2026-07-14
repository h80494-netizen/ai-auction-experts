import sqlite3

DB_PATH = "c:/Users/llll/Documents/두인경매/바이브코딩/backend/data/map_data.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# IDs to delete from redevelopment_zones based on our findings
ids_to_delete = [588, 708, 714, 1740, 1990, 2254]

print(f"Deleting the following IDs from redevelopment_zones: {ids_to_delete}")
cursor.execute(f"DELETE FROM redevelopment_zones WHERE id IN ({','.join(map(str, ids_to_delete))})")

# Also delete from district_units just in case
cursor.execute("DELETE FROM district_units WHERE name LIKE '%은평뉴타운%' OR name IN ('은평1지구', '은평2지구', '은평3-1지구', '은평3-2지구', '은평재정비촉진지구')")

# Also delete from zoning_polygons just in case
cursor.execute("DELETE FROM zoning_polygons WHERE name LIKE '%은평뉴타운%' OR name IN ('은평1지구', '은평2지구', '은평3-1지구', '은평3-2지구', '은평재정비촉진지구')")

conn.commit()
conn.close()

print("Deletion complete.")
