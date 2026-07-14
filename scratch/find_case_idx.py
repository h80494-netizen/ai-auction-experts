import sqlite3
import os

db_paths = [
    'backend/data/map_data.db',
    'backend/map_data.db',
    'map_data.db',
    'backend/auction_data.db',
    'backend/data.db'
]

for path in db_paths:
    if os.path.exists(path):
        print(f"Searching in {path}...")
        try:
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            
            # get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in cursor.fetchall()]
            
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                cols = [c[1] for c in cursor.fetchall()]
                
                # construct query based on column names
                q_cols = []
                for c in cols:
                    if 'case_number' in c or 'case_no' in c or '사건번호' in c or 'id' in c or 'idx' in c or 'info' in c or 'address' in c:
                        q_cols.append(c)
                
                if q_cols:
                    # Search
                    for col in cols:
                        try:
                            cursor.execute(f"SELECT * FROM {table} WHERE CAST({col} AS TEXT) LIKE '%100709%'")
                            rows = cursor.fetchall()
                            if rows:
                                print(f"  Table: {table}, Column: {col} -> Found {len(rows)} matching rows:")
                                for r in rows[:3]:
                                    print("   ", r[:5])
                        except Exception as query_err:
                            pass
            conn.close()
        except Exception as e:
            print(f"Error reading {path}: {e}")
