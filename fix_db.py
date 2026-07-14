import sqlite3

conn = sqlite3.connect('backend/data/map_data.db')
cursor = conn.cursor()

# Find the columns to build conditions safely
cursor.execute("PRAGMA table_info(redevelopment_zones)")
cols = [c[1] for c in cursor.fetchall()]

conditions = []
if 'title' in cols: conditions.append("title LIKE '%은평뉴타운%'")
if 'bsns_nm' in cols: conditions.append("bsns_nm LIKE '%은평뉴타운%'")
if 'name' in cols: conditions.append("name LIKE '%은평뉴타운%'")

if conditions:
    query = f"UPDATE redevelopment_zones SET propel_cd='FINISHED' WHERE {' OR '.join(conditions)}"
    cursor.execute(query)
    print(f"Rows updated: {cursor.rowcount}")
    conn.commit()
else:
    print("No matching columns found.")

conn.close()
