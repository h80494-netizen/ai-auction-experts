import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    conn = sqlite3.connect('backend/data/map_data.db')
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM crosswalk_segments")
    count = cur.fetchone()[0]
    print(f"Total crosswalk segments: {count}")
    
    # Check coords_json lat/lng ranges
    cur.execute("SELECT MIN(min_lat), MAX(max_lat), MIN(min_lng), MAX(max_lng) FROM crosswalk_segments")
    bounds = cur.fetchone()
    print(f"Bounds in crosswalk_segments: min_lat={bounds[0]}, max_lat={bounds[1]}, min_lng={bounds[2]}, max_lng={bounds[3]}")
    
    conn.close()

if __name__ == '__main__':
    main()
