import sqlite3
import json

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT propel_cd, COUNT(*) FROM redevelopment_zones GROUP BY propel_cd")
codes_counts = cursor.fetchall()
codes_counts.sort(key=lambda x: x[1], reverse=True)

with open('scratch/redevelopment_samples.txt', 'w', encoding='utf-8') as f:
    f.write("Redevelopment zones propel_cd and name samples:\n")
    for code, count in codes_counts:
        cursor.execute("SELECT name FROM redevelopment_zones WHERE propel_cd = ? LIMIT 5", (code,))
        names = [r[0] for r in cursor.fetchall()]
        f.write(f"Code: {code} (Count: {count})\n")
        for name in names:
            f.write(f"  - {name}\n")
        f.write("\n")

print("Done writing redevelopment samples to scratch/redevelopment_samples.txt")
conn.close()
