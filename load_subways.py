import sqlite3
import pandas as pd
import sys

def main():
    try:
        conn = sqlite3.connect('backend/data/map_data.db')
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS subways")
        cursor.execute("CREATE TABLE subways (id INTEGER PRIMARY KEY, line TEXT, name TEXT, address TEXT, lat REAL, lng REAL)")

        df = pd.read_excel('지하철정보_260425.xlsx', 'Sheet1')
        df.columns = [c.strip() for c in df.columns]

        for _, row in df.iterrows():
            cursor.execute("INSERT INTO subways (line, name, address, lat, lng) VALUES (?, ?, ?, ?, ?)",
                (str(row.get('노선', '')), str(row.get('지하철명', '')), str(row.get('지번주소', '')), float(row.get('위도', 0)), float(row.get('경도', 0)))
            )

        conn.commit()
        conn.close()
        print("Subways loaded successfully!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
