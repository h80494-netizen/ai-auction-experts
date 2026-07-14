import sqlite3
import os

db_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"

if not os.path.exists(db_path):
    print("Database not found!")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in map_data.db:", tables)

for table in tables:
    try:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [row['name'] for row in cursor.fetchall()]
        
        # Build search query for any column containing '수진' or '태평'
        where_clauses = []
        params = []
        for col in cols:
            where_clauses.append(f"CAST({col} AS TEXT) LIKE ?")
            params.append("%수진%")
            where_clauses.append(f"CAST({col} AS TEXT) LIKE ?")
            params.append("%태평%")
        
        if where_clauses:
            sql = f"SELECT * FROM {table} WHERE " + " OR ".join(where_clauses)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            if rows:
                print(f"\n[MATCH] Table: {table} | Found {len(rows)} matching rows:")
                for row in rows[:10]: # limit print to 10
                    # We can print standard columns but truncate long geom/geojson strings
                    d = dict(row)
                    for k, v in d.items():
                        if isinstance(v, str) and len(v) > 150:
                            d[k] = v[:100] + "... (truncated)"
                    print("  ", d)
                if len(rows) > 10:
                    print(f"  ... and {len(rows)-10} more rows")
    except Exception as e:
        print(f"Error querying table {table}: {e}")

conn.close()
