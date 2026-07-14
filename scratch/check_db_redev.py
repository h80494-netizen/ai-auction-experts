import sqlite3
import os

databases = ['backend/map_data.db', 'backend/data.db']

for db_path in databases:
    if not os.path.exists(db_path):
        print(f"DB does not exist: {db_path}")
        continue
        
    print(f"\n=========================================")
    print(f"Checking Database: {db_path}")
    print(f"=========================================")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in DB:", tables)
        
        for table_tuple in tables:
            table_name = table_tuple[0]
            if 'redevelopment' in table_name or 'zone' in table_name or 'taekji' in table_name:
                print(f"\nSearching in table: {table_name}")
                cursor.execute(f"PRAGMA table_info({table_name});")
                cols = [c[1] for c in cursor.fetchall()]
                print("Columns:", cols)
                
                # Check for Sujin (수진) and Taepyeong (태평)
                # We can check name columns if they exist. Let's find columns that might contain name.
                name_col = 'name' if 'name' in cols else (cols[0] if cols else '')
                if name_col:
                    cursor.execute(f"SELECT * FROM {table_name} WHERE {name_col} LIKE '%수진%' OR {name_col} LIKE '%태평%';")
                    rows = cursor.fetchall()
                    print(f"Found {len(rows)} matches:")
                    for r in rows:
                        r_display = []
                        for i, val in enumerate(r):
                            val_str = str(val)
                            if len(val_str) > 100:
                                r_display.append(val_str[:50] + "... (truncated)")
                            else:
                                r_display.append(val)
                        print(r_display)
                else:
                    print("No queryable name column found.")
                    
    except Exception as e:
        print("Error querying database:", e)
    finally:
        if 'conn' in locals():
            conn.close()
