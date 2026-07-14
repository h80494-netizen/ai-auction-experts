import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT DISTINCT propel_cd FROM redevelopment_zones")
codes = [r[0] for r in c.fetchall() if r[0]]

# Let's inspect codes where we are unsure of the stage, e.g. PP08xx, PP09xx, PP10xx, PP11xx, PP12xx, PP13xx, PP14xx, PP15xx, PP16xx, PP18xx, PP19xx, PP20xx, PP21xx
print("Inspecting stage names for various propel_cd:")
for prefix in ['PP04', 'PP05', 'PP06', 'PP07', 'PP08', 'PP09', 'PP10', 'PP11', 'PP12', 'PP13', 'PP14', 'PP15', 'PP16', 'PP18', 'PP19', 'PP20', 'PP21']:
    matching_codes = [c for c in codes if c.startswith(prefix)]
    if not matching_codes:
        continue
    print(f"\n=== Group {prefix} ===")
    for code in sorted(matching_codes):
        c.execute("SELECT name FROM redevelopment_zones WHERE propel_cd = ? LIMIT 3", (code,))
        names = [r[0] for r in c.fetchall()]
        print(f"Code {code}:")
        for name in names:
            print(f"  {name}")

conn.close()
