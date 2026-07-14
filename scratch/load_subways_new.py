import sqlite3
import pandas as pd
import sys
import os

DB_PATH = 'backend/data/map_data.db'

def main():
    try:
        if not os.path.exists(DB_PATH):
            print(f"Error: Database file not found at {DB_PATH}")
            sys.exit(1)
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Recreate subways table with the status (상황) column
        cursor.execute("DROP TABLE IF EXISTS subways")
        cursor.execute("""
            CREATE TABLE subways (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                line TEXT,
                name TEXT,
                address TEXT,
                lat REAL,
                lng REAL,
                status TEXT
            )
        """)

        # Load Excel sheet
        xls_path = 'data/지하철역사.xlsx'
        print(f"Loading Excel file from {xls_path}...")
        df = pd.read_excel(xls_path, sheet_name='예정역포함')
        
        # Clean column names (strip spaces)
        df.columns = [c.strip() for c in df.columns]
        print("Cleaned Columns:", df.columns.tolist())

        count = 0
        for _, row in df.iterrows():
            line = str(row.get('노선', '')).strip()
            name = str(row.get('지하철명', '')).strip()
            address = str(row.get('지번주소', '')).strip()
            lat_val = row.get('위도', 0)
            lng_val = row.get('경도', 0)
            status = str(row.get('상황', '기존')).strip()

            # Robust coordinate parsing
            try:
                lat = float(lat_val)
            except (ValueError, TypeError):
                lat = 0.0
            try:
                lng = float(lng_val)
            except (ValueError, TypeError):
                lng = 0.0

            if not line or not name:
                continue

            cursor.execute(
                "INSERT INTO subways (line, name, address, lat, lng, status) VALUES (?, ?, ?, ?, ?, ?)",
                (line, name, address, lat, lng, status)
            )
            count += 1

        conn.commit()
        conn.close()
        print(f"Successfully loaded {count} subway stations into subways table!")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
