import sqlite3
import os

db_dir = 'backend/data'
dbs = [f for f in os.listdir(db_dir) if f.endswith('.db')]

for db_name in dbs:
    db_path = os.path.join(db_dir, db_name)
    print(f"\n=================== DATABASE: {db_name} ===================")
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        for t in tables:
            t_name = t[0]
            c.execute(f"PRAGMA table_info({t_name})")
            cols = [col[1] for col in c.fetchall()]
            c.execute(f"SELECT COUNT(*) FROM {t_name}")
            row_count = c.fetchone()[0]
            print(f"Table: {t_name} ({row_count} rows)")
            print(f"  Columns: {cols}")
        conn.close()
    except Exception as e:
        print(f"Error reading {db_name}: {e}")
