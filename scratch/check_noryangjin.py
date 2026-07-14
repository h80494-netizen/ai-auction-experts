import sqlite3
import os

db_path = os.path.abspath(os.path.join('backend', 'data', 'map_data.db'))
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(redevelopment_zones)")
cols = [c[1] for c in cursor.fetchall()]

conditions = []
select_cols = ["rowid", "propel_cd"]
if 'title' in cols: 
    conditions.append("title LIKE '%노량진%'")
    select_cols.append("title")
if 'bsns_nm' in cols: 
    conditions.append("bsns_nm LIKE '%노량진%'")
    select_cols.append("bsns_nm")
if 'name' in cols: 
    conditions.append("name LIKE '%노량진%'")
    select_cols.append("name")

if conditions:
    query = f"SELECT {', '.join(select_cols)} FROM redevelopment_zones WHERE {' OR '.join(conditions)}"
    cursor.execute(query)
    rows = cursor.fetchall()
    print("Found Noryangjin rows:")
    for row in rows:
        print(row)
else:
    print("No matching columns found.")

conn.close()
