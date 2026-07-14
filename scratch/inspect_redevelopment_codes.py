import sqlite3
from collections import Counter

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get unique propel_cd values and count
cursor.execute("SELECT propel_cd, COUNT(*) FROM redevelopment_zones GROUP BY propel_cd")
results = cursor.fetchall()
results.sort(key=lambda x: x[1], reverse=True)

print("Unique propel_cd in redevelopment_zones:")
for code, count in results:
    print(f"Code: {code}, Count: {count}")

# Also print a sample of names for some of the codes
print("\nSamples by code:")
for code, _ in results[:10]:
    if code:
        cursor.execute("SELECT name, propel_cd FROM redevelopment_zones WHERE propel_cd = ? LIMIT 3", (code,))
        samples = cursor.fetchall()
        print(f"Code {code}: {samples}")

conn.close()
