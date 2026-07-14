import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'map_data.db'))
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Try to find Eunpyeong New Town
# The table might be redevelopment_zones
# Columns might be objectid, pnu, name, title, bsns_nm, etc.
# Let's check columns first
cursor.execute("PRAGMA table_info(redevelopment_zones)")
columns = [col[1] for col in cursor.fetchall()]

# Build conditions based on columns
conditions = []
if 'title' in columns: conditions.append("title LIKE '%은평뉴타운%'")
if 'bsns_nm' in columns: conditions.append("bsns_nm LIKE '%은평뉴타운%'")
if 'name' in columns: conditions.append("name LIKE '%은평뉴타운%'")
if 'bjdong_nm' in columns: conditions.append("bjdong_nm LIKE '%진관%'")
if 'gu_nm' in columns: conditions.append("gu_nm LIKE '%은평%'")

query = f"SELECT rowid, * FROM redevelopment_zones WHERE {' OR '.join(conditions)}"
try:
    cursor.execute(query)
    rows = cursor.fetchall()
    print(f"Found {len(rows)} rows for Eunpyeong New Town.")
    
    # Update propel_cd to 'FINISHED' for all found rows
    if rows:
        row_ids = [row[0] for row in rows]
        placeholders = ','.join('?' * len(row_ids))
        cursor.execute(f"UPDATE redevelopment_zones SET propel_cd='FINISHED' WHERE rowid IN ({placeholders})", row_ids)
        print(f"Updated {cursor.rowcount} rows to FINISHED stage.")
        conn.commit()
except Exception as e:
    print(f"Error: {e}")

conn.close()
