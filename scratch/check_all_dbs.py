import sqlite3
import os

def check_db(path):
    if not os.path.exists(path):
        print(f"Path does not exist: {path}")
        return
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        
        # Check if tables exist
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cur.fetchall()]
        
        print(f"\nDB: {path}")
        print(f"Tables: {tables}")
        
        if 'crosswalk_segments' in tables:
            cur.execute("SELECT COUNT(*) FROM crosswalk_segments")
            count = cur.fetchone()[0]
            print(f"  crosswalk_segments count: {count}")
        else:
            print("  crosswalk_segments table NOT FOUND")
            
        if 'subways' in tables:
            cur.execute("SELECT COUNT(*) FROM subways")
            count = cur.fetchone()[0]
            print(f"  subways count: {count}")
            cur.execute("SELECT id, name, lat, lng FROM subways WHERE name LIKE '%내방%'")
            print("  Naebang in subways:", cur.fetchall())
        else:
            print("  subways table NOT FOUND")
            
        conn.close()
    except Exception as e:
        print(f"Error checking {path}: {e}")

def main():
    paths = [
        'map_data.db',
        'backend/map_data.db',
        'backend/data/map_data.db'
    ]
    for p in paths:
        check_db(p)

if __name__ == '__main__':
    main()
