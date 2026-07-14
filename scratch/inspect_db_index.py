import sqlite3
import os

DB_PATH = 'backend/data/map_data.db'
if not os.path.exists(DB_PATH):
    print('DB does not exist at:', DB_PATH)
else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    print('Tables:', tables)
    
    # List all indexes
    cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index'")
    indexes = cursor.fetchall()
    print('\nIndexes:')
    for idx in indexes:
        print(f'Index Name: {idx[0]}, Table: {idx[1]}')
        print(f'  SQL: {idx[2]}')
        
    # Check table info
    for tbl in ['redevelopment_zones', 'zoning_polygons', 'planning_roads']:
        if tbl in tables:
            print(f'\nSchema of {tbl}:')
            cursor.execute(f"PRAGMA table_info({tbl})")
            for col in cursor.fetchall():
                print(f'  {col[1]} ({col[2]})')
    conn.close()
