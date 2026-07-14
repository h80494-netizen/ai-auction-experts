import sqlite3
import os

db_path = 'backend/data/map_data.db'
if not os.path.exists(db_path):
    print("Database file not found at:", os.path.abspath(db_path))
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 테이블 목록 조회
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print('Tables in DB:', tables)

# crosswalk_segments 정보 확인
if 'crosswalk_segments' in tables:
    cursor.execute("PRAGMA table_info(crosswalk_segments)")
    print('crosswalk_segments columns:', cursor.fetchall())
    cursor.execute("SELECT COUNT(*) FROM crosswalk_segments")
    print('crosswalk_segments count:', cursor.fetchone()[0])
    cursor.execute("SELECT * FROM crosswalk_segments LIMIT 3")
    print('crosswalk_segments sample:')
    for row in cursor.fetchall():
        print(row)
else:
    print('crosswalk_segments table NOT FOUND')

# road_cache_segments 내 highway 종류 확인
if 'road_cache_segments' in tables:
    cursor.execute("SELECT highway, COUNT(*) FROM road_cache_segments GROUP BY highway")
    print('road_cache_segments highway values:', cursor.fetchall())
    cursor.execute("SELECT COUNT(*) FROM road_cache_segments WHERE highway = '횡단보도' OR name = '횡단보도'")
    print('Count where highway/name is 횡단보도:', cursor.fetchone()[0])
    cursor.execute("SELECT COUNT(*) FROM road_cache_segments WHERE highway = 'crossing'")
    print('Count where highway is crossing:', cursor.fetchone()[0])
    
conn.close()
