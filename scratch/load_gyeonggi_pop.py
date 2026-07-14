import sqlite3
import pandas as pd
import sys
import os
import re

DB_PATH = 'backend/data/map_data.db'
EXCEL_PATH = 'data/경기유동인구_행정동단위집계.xls'

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

        # Re-create gyeonggi_dong_population table
        print("Re-creating gyeonggi_dong_population table...")
        cursor.execute("DROP TABLE IF EXISTS gyeonggi_dong_population")
        cursor.execute("""
            CREATE TABLE gyeonggi_dong_population (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sgg TEXT,
                dong TEXT,
                lat REAL,
                lng REAL,
                population REAL
            )
        """)

        # Get all auctions for coordinate lookup
        print("Fetching coordinates from auctions table...")
        cursor.execute("SELECT address, lat, lng FROM auctions WHERE lat IS NOT NULL AND lng IS NOT NULL")
        auctions = cursor.fetchall()

        # Get all bus stops for coordinate lookup
        print("Fetching coordinates from bus_stops table...")
        cursor.execute("SELECT name, city, lat, lng, address FROM bus_stops WHERE lat IS NOT NULL AND lng IS NOT NULL")
        bus_stops = cursor.fetchall()

        # Load Excel file
        print("Loading Excel file...")
        df = pd.read_excel(EXCEL_PATH, sheet_name='유동인구_행정동 단위 집계')
        df.columns = [c.strip() for c in df.columns]

        # Age/gender columns are everything except the metadata columns
        meta_cols = ['행정동코드', '시도명', '시군구명', '행정동명', '시간대별', '내외국인구분', '기준년월일']
        pop_cols = [c for c in df.columns if c not in meta_cols]
        print(f"Found {len(pop_cols)} population columns.")

        # Compute row totals
        df['row_total'] = df[pop_cols].sum(axis=1)

        # Group by sgg and dong to compute average total population
        print("Grouping and computing average total population...")
        grouped = df.groupby(['시군구명', '행정동명'])['row_total'].mean().reset_index()
        print(f"Total administrative dongs: {len(grouped)}")

        count = 0
        records = []
        for _, row in grouped.iterrows():
            sgg = str(row['시군구명']).strip()
            dong = str(row['행정동명']).strip()
            population = float(row['row_total'])

            # Multi-stage lookup for lat/lng
            dong_clean = re.sub(r'\d+동$', '동', dong)
            dong_base = dong.replace('동', '')

            lat, lng = None, None

            # Stage 1: Try auctions
            matching_coords = []
            for addr, a_lat, a_lng in auctions:
                if sgg in addr and (dong in addr or dong_clean in addr or dong_base in addr):
                    matching_coords.append((a_lat, a_lng))
            
            if matching_coords:
                lat = sum(c[0] for c in matching_coords) / len(matching_coords)
                lng = sum(c[1] for c in matching_coords) / len(matching_coords)
            
            # Stage 2: Try bus stops
            if lat is None:
                matching_bus = []
                for b_name, b_city, b_lat, b_lng, b_addr in bus_stops:
                    if sgg in b_city and (dong in b_name or dong in b_addr or dong_clean in b_addr or dong_base in b_addr):
                        matching_bus.append((b_lat, b_lng))
                
                if matching_bus:
                    lat = sum(c[0] for c in matching_bus) / len(matching_bus)
                    lng = sum(c[1] for c in matching_bus) / len(matching_bus)

            # Stage 3: Fallback to district average (auctions)
            if lat is None:
                matching_district = []
                for addr, a_lat, a_lng in auctions:
                    if sgg in addr:
                        matching_district.append((a_lat, a_lng))
                
                if matching_district:
                    lat = sum(c[0] for c in matching_district) / len(matching_district)
                    lng = sum(c[1] for c in matching_district) / len(matching_district)

            # Stage 4: Fallback to district average (bus stops)
            if lat is None:
                matching_district_bus = []
                for b_name, b_city, b_lat, b_lng, b_addr in bus_stops:
                    if sgg in b_city:
                        matching_district_bus.append((b_lat, b_lng))
                
                if matching_district_bus:
                    lat = sum(c[0] for c in matching_district_bus) / len(matching_district_bus)
                    lng = sum(c[1] for c in matching_district_bus) / len(matching_district_bus)

            # Absolute fallback to Gyeonggi Province Center
            if lat is None:
                lat, lng = 37.2752, 127.0094 # Suwon center

            records.append((sgg, dong, lat, lng, population))
            count += 1

        cursor.executemany(
            "INSERT INTO gyeonggi_dong_population (sgg, dong, lat, lng, population) VALUES (?, ?, ?, ?, ?)",
            records
        )
        conn.commit()
        conn.close()

        print(f"Successfully loaded {count} Gyeonggi dong population records into SQLite!")

    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
