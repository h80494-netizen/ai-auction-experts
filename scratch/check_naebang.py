import sqlite3
import sys
import io

# Set stdout/stderr to utf-8 to avoid encoding issues in python prints
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    conn = sqlite3.connect('backend/data/map_data.db')
    cur = conn.cursor()
    cur.execute("SELECT id, line, name, address, lat, lng FROM subways WHERE name LIKE '%내방%'")
    rows = cur.fetchall()
    print("Naebang station rows:")
    for row in rows:
        print(f"id={row[0]}, line={row[1]}, name={row[2]}, address={row[3]}, lat={row[4]}, lng={row[5]}")
    conn.close()

if __name__ == '__main__':
    main()
