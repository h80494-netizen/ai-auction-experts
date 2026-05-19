import pandas as pd
import sqlite3
import os

EXCEL_PATH = os.path.join(os.path.dirname(__file__), '../../data/GPS주소와 거리찾기_260504.xlsx')
BUS_CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/국토교통부_전국 버스정류장 위치정보_20251031.csv')
HS_RATE_PATH = os.path.join(os.path.dirname(__file__), '../../특목고진학률.xlsx')
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/map_data.db')

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subways (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            line TEXT,
            name TEXT,
            address TEXT,
            lat REAL,
            lng REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS universities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            lat REAL,
            lng REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS middle_schools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            lat REAL,
            lng REAL,
            special_hs_rate REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS industrial_complexes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            lat REAL,
            lng REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bus_stops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            city TEXT,
            lat REAL,
            lng REAL
        )
    ''')
    cursor.execute('DELETE FROM subways')
    cursor.execute('DELETE FROM universities')
    cursor.execute('DELETE FROM middle_schools')
    cursor.execute('DELETE FROM industrial_complexes')
    cursor.execute('DELETE FROM bus_stops')
    conn.commit()

def import_data():
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    cursor = conn.cursor()

    # Load Special HS Entrance Rates
    print("Loading Middle School Entrance Rates...")
    hs_rates = {}
    try:
        df_hs = pd.read_excel(HS_RATE_PATH, sheet_name=1, header=1) # The headers are on the second row
        for idx, row in df_hs.iterrows():
            school_name = str(row.get('학교명', '')).strip()
            rate_val = row.get('비율', 0.0)
            if pd.notna(rate_val) and school_name:
                # Convert ratio (0.817) to percentage (81.7%)
                hs_rates[school_name] = round(float(rate_val) * 100, 2)
    except Exception as e:
        print(f"Failed to load entrance rates: {e}")

    print("Loading Excel file...")
    xls = pd.ExcelFile(EXCEL_PATH)
    
    print("Processing Subways...")
    df_subway = pd.read_excel(xls, '지하철역')
    count_sub = 0
    for idx, row in df_subway.iterrows():
        try:
            lat = float(row.get(' 위도 ', 0))
            lng = float(row.get(' 경도 ', 0))
            if pd.notna(lat) and pd.notna(lng) and lat > 0:
                line = str(row.get('노선', ''))
                name = str(row.get('지하철명', ''))
                addr = str(row.get('지번주소', ''))
                cursor.execute('INSERT INTO subways (line, name, address, lat, lng) VALUES (?, ?, ?, ?, ?)',
                               (line, name, addr, lat, lng))
                count_sub += 1
        except Exception:
            pass
            
    print("Processing Universities...")
    df_univ = pd.read_excel(xls, '대학', header=None, skiprows=1)
    count_univ = 0
    for idx, row in df_univ.iterrows():
        try:
            lat = float(row[6])
            lng = float(row[3])
            if pd.notna(lat) and pd.notna(lng) and lat > 0:
                name = str(row[0])
                addr = str(row[1])
                cursor.execute('INSERT INTO universities (name, address, lat, lng) VALUES (?, ?, ?, ?)',
                               (name, addr, lat, lng))
                count_univ += 1
        except Exception:
            pass

    print("Processing Middle Schools (Seoul, Gyeonggi, Incheon only)...")
    df_middle = pd.read_excel(xls, '중학교', header=None, skiprows=1)
    count_mid = 0
    for idx, row in df_middle.iterrows():
        try:
            lat = float(row[6])
            lng = float(row[3])
            addr = str(row[1])
            
            # Filter for Seoul, Gyeonggi, Incheon
            if any(region in addr for region in ['서울', '경기', '인천']):
                if pd.notna(lat) and pd.notna(lng) and lat > 0:
                    name = str(row[0])
                    # Lookup rate
                    special_hs_rate = hs_rates.get(name.strip(), 0.0)
                    
                    cursor.execute('INSERT INTO middle_schools (name, address, lat, lng, special_hs_rate) VALUES (?, ?, ?, ?, ?)',
                                   (name, addr, lat, lng, special_hs_rate))
                    count_mid += 1
        except Exception:
            pass

    print("Processing Industrial Complexes...")
    df_ind = pd.read_excel(xls, '산단', header=None, skiprows=1)
    count_ind = 0
    for idx, row in df_ind.iterrows():
        try:
            lat = float(row[1])
            lng = float(row[2])
            if pd.notna(lat) and pd.notna(lng) and lat > 0:
                name = str(row[0])
                cursor.execute('INSERT INTO industrial_complexes (name, lat, lng) VALUES (?, ?, ?)',
                               (name, lat, lng))
                count_ind += 1
        except Exception:
            pass

    print("Processing Bus Stops (Seoul, Gyeonggi, Incheon only)...")
    count_bus = 0
    try:
        chunksize = 10000
        for chunk in pd.read_csv(BUS_CSV_PATH, encoding='cp949', chunksize=chunksize):
            for idx, row in chunk.iterrows():
                try:
                    city = str(row.get('도시명', ''))
                    # Filter for Seoul, Gyeonggi, Incheon
                    if any(region in city for region in ['서울', '경기', '인천']):
                        lat = float(row.get('위도', 0))
                        lng = float(row.get('경도', 0))
                        name = str(row.get('정류장명', ''))
                        if lat > 0 and lng > 0:
                            cursor.execute('INSERT INTO bus_stops (name, city, lat, lng) VALUES (?, ?, ?, ?)',
                                           (name, city, lat, lng))
                            count_bus += 1
                except Exception:
                    pass
    except Exception as e:
        print(f"Failed to load bus stops: {e}")

    conn.commit()
    
    # Create indexes for fast bounding box queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bus_lat_lng ON bus_stops(lat, lng)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_mid_lat_lng ON middle_schools(lat, lng)')
    conn.commit()
    conn.close()
    
    print(f"Import completed! Subways: {count_sub}, Univ: {count_univ}, Middle: {count_mid}, Ind: {count_ind}, Bus: {count_bus}")

if __name__ == '__main__':
    import_data()
