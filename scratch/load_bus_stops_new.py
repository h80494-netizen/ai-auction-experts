import sqlite3
import pandas as pd
import sys
import os

DB_PATH = 'backend/data/map_data.db'
EXCEL_PATH = 'data/경기버스정류소현황.xls'

def main():
    try:
        if not os.path.exists(DB_PATH):
            print(f"Error: Database file not found at {DB_PATH}")
            sys.exit(1)
        if not os.path.exists(EXCEL_PATH):
            print(f"Error: Excel file not found at {EXCEL_PATH}")
            sys.exit(1)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Fetch and preserve Seoul bus stops
        print("Fetching existing Seoul bus stops...")
        cursor.execute("""
            SELECT name, city, lat, lng 
            FROM bus_stops 
            WHERE city LIKE '%서울%' OR city LIKE '%특별시%'
        """)
        seoul_stops = cursor.fetchall()
        print(f"Found {len(seoul_stops)} Seoul bus stops to preserve.")

        # 2. Re-create the bus_stops table with address column
        print("Re-creating bus_stops table...")
        cursor.execute("DROP TABLE IF EXISTS bus_stops")
        cursor.execute("""
            CREATE TABLE bus_stops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                city TEXT,
                lat REAL,
                lng REAL,
                address TEXT
            )
        """)

        # 3. Restore Seoul bus stops (setting empty string for address)
        if seoul_stops:
            print("Restoring Seoul bus stops...")
            seoul_records = [(r[0], r[1], r[2], r[3], '') for r in seoul_stops]
            cursor.executemany(
                "INSERT INTO bus_stops (name, city, lat, lng, address) VALUES (?, ?, ?, ?, ?)",
                seoul_records
            )
            print(f"Restored {len(seoul_stops)} Seoul bus stops.")

        # 4. Load Gyeonggi bus stops from Excel
        print("Loading Gyeonggi bus stops from Excel...")
        df = pd.read_excel(EXCEL_PATH, sheet_name='버스정류소 현황')
        df.columns = [c.strip() for c in df.columns]
        
        count = 0
        records = []
        for _, row in df.iterrows():
            name = str(row.get('정류소명', '')).strip()
            city = str(row.get('시군명', '')).strip()
            lat_val = row.get('WGS84위도', 0)
            lng_val = row.get('WGS84경도', 0)
            address = str(row.get('위치', '')).strip()

            try:
                lat = float(lat_val)
            except:
                lat = 0.0
            try:
                lng = float(lng_val)
            except:
                lng = 0.0

            if not name:
                continue

            # Ensure Gyeonggi prefix is on the city name or keep it clean
            city_name = f"경기도 {city}" if not city.startswith("경기") else city
            records.append((name, city_name, lat, lng, address))
            count += 1

        cursor.executemany(
            "INSERT INTO bus_stops (name, city, lat, lng, address) VALUES (?, ?, ?, ?, ?)",
            records
        )
        conn.commit()
        conn.close()
        
        print(f"Successfully loaded {count} Gyeonggi bus stops!")
        print(f"Total bus stops in table: {len(seoul_stops) + count}")

    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
