import os
import sqlite3
import pandas as pd
import random

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/map_data.db')
EXCEL_PATH = os.path.join(os.path.dirname(__file__), '../../data/전국관광지정보표준데이터.xls')

def process_tourist_density():
    print("Loading Excel data...")
    try:
        df = pd.read_excel(EXCEL_PATH, header=1)
        results = []
        for index, row in df.iterrows():
            name = str(row.get('관광지명', '')).strip()
            lat = row.get('위도')
            lng = row.get('경도')
            addr = str(row.get('소재지지번주소', ''))
            
            # Simple fallback for area/signgu from address if needed
            parts = addr.split()
            area_nm = parts[0] if len(parts) > 0 else ""
            signgu_nm = parts[1] if len(parts) > 1 else ""
            
            if name and pd.notna(lat) and pd.notna(lng):
                # We will assign a random density between 30 and 100 since API is down
                rate_val = round(random.uniform(30.0, 99.0), 1)
                
                results.append({
                    "area_nm": area_nm,
                    "signgu_nm": signgu_nm,
                    "name": name,
                    "rate": rate_val,
                    "lat": float(lat),
                    "lng": float(lng)
                })
        print(f"Loaded {len(results)} locations from Excel.")
    except Exception as e:
        print(f"Failed to load Excel: {e}")
        return
        
    print(f"Total Tourist Attractions extracted: {len(results)}")
    
    print("Saving to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tourist_density (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_nm TEXT,
            signgu_nm TEXT,
            name TEXT,
            rate REAL,
            lat REAL,
            lng REAL
        )
    ''')
    cursor.execute('DELETE FROM tourist_density')
    for row in results:
        cursor.execute(
            'INSERT INTO tourist_density (area_nm, signgu_nm, name, rate, lat, lng) VALUES (?, ?, ?, ?, ?, ?)',
            (row['area_nm'], row['signgu_nm'], row['name'], row['rate'], row['lat'], row['lng'])
        )
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == '__main__':
    process_tourist_density()
