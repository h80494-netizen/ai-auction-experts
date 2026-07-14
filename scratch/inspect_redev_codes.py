import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT DISTINCT propel_cd FROM redevelopment_zones")
codes = [r[0] for r in c.fetchall() if r[0]]

print("Sample zones for each code:")
for code in sorted(codes):
    c.execute("SELECT name FROM redevelopment_zones WHERE propel_cd = ? LIMIT 3", (code,))
    names = [r[0] for r in c.fetchall()]
    print(f"Code {code}:")
    for name in names:
        print(f"  - {name}")

conn.close()
