import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT DISTINCT propel_cd FROM redevelopment_zones")
codes = [r[0] for r in c.fetchall() if r[0]]

with open('scratch/inspect_redev_clean.txt', 'w', encoding='utf-8') as f:
    f.write("Inspecting stage names for various propel_cd:\n")
    for prefix in ['PP01', 'PP02', 'PP03', 'PP04', 'PP05', 'PP06', 'PP07', 'PP08', 'PP09', 'PP10', 'PP11', 'PP12', 'PP13', 'PP14', 'PP15', 'PP16', 'PP18', 'PP19', 'PP20', 'PP21']:
        matching_codes = [c for c in codes if c.startswith(prefix)]
        if not matching_codes:
            continue
        f.write(f"\n=== Group {prefix} ===\n")
        for code in sorted(matching_codes):
            c.execute("SELECT name FROM redevelopment_zones WHERE propel_cd = ? LIMIT 3", (code,))
            names = [r[0] for r in c.fetchall()]
            f.write(f"Code {code}:\n")
            for name in names:
                f.write(f"  {name}\n")

print("Saved clean output to scratch/inspect_redev_clean.txt")
conn.close()
