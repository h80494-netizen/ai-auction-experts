import sqlite3
import pandas as pd
import sys
import os

DB_PATH = 'backend/data/map_data.db'
EXCEL_PATH = 'data/지하철역1(위례과천선포함).xlsx'

# If '지하철역사1(위례과천선포함).xlsx' exists, use it. Otherwise, use '지하철역1(위례과천선포함).xlsx'
if os.path.exists('data/지하철역사1(위례과천선포함).xlsx'):
    EXCEL_PATH = 'data/지하철역사1(위례과천선포함).xlsx'
elif os.path.exists('data/지하철역1(위례과천선포함).xlsx'):
    EXCEL_PATH = 'data/지하철역1(위례과천선포함).xlsx'

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

        # Recreate subways table
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

        print(f"Loading Sheet 1 (전국_노선망_종합분석) from {EXCEL_PATH}...")
        df = pd.read_excel(EXCEL_PATH, sheet_name='전국_노선망_종합분석', header=2)
        
        # Strip whitespaces from column names
        df.columns = [str(c).strip() for c in df.columns]

        count = 0
        for _, row in df.iterrows():
            line = str(row.iloc[1]).strip()
            name = str(row.iloc[2]).strip()
            address = str(row.iloc[3]).strip()
            lat_val = row.iloc[4]
            lng_val = row.iloc[5]
            status = str(row.iloc[6]).strip()

            if not line or not name or line == 'nan' or name == 'nan':
                continue

            try:
                lat = float(lat_val)
            except:
                lat = 0.0
            try:
                lng = float(lng_val)
            except:
                lng = 0.0

            # Normalize status to standard ones: '기존', '개발 예정 (신설)', '개발 예정 (예정)', '개발 예정 (연장)'
            if '정상 운영 중' in status or '이미 완공됨' in status or '★이미 완공됨' in status:
                status_norm = '기존'
            elif '신설' in status:
                status_norm = '개발 예정 (신설)'
            elif '예정' in status:
                status_norm = '개발 예정 (예정)'
            elif '연장' in status:
                status_norm = '개발 예정 (연장)'
            else:
                status_norm = '기존'

            cursor.execute(
                "INSERT INTO subways (line, name, address, lat, lng, status) VALUES (?, ?, ?, ?, ?, ?)",
                (line, name, address, lat, lng, status_norm)
            )
            count += 1

        print(f"Successfully loaded {count} subway stations from Sheet 1.")

        print("Inserting custom '위례과천선' stations from Sheet 2 plans...")
        # Define Wirye-Gwacheon line stations explicitly with robust coordinates
        wirye_gwacheon_stations = [
            {"name": "정부과천청사역", "address": "경기도 과천시 중앙동 일원", "lat": 37.427489, "lng": 126.991422, "status": "기존"},
            {"name": "문원역(가칭)", "address": "경기도 과천시 문원동 일원", "lat": 37.4222, "lng": 127.0031, "status": "개발 예정 (신설)"},
            {"name": "과천주암역(가칭)", "address": "경기도 과천시 주암동 일원", "lat": 37.4501, "lng": 127.0201, "status": "개발 예정 (신설)"},
            {"name": "우면역(가칭)", "address": "서울 서초구 우면동 일원", "lat": 37.4595, "lng": 127.0275, "status": "개발 예정 (신설)"},
            {"name": "양재시민의숲역", "address": "서울 서초구 양재동 일원", "lat": 37.469973, "lng": 127.038327, "status": "기존"},
            {"name": "포이역(가칭)", "address": "서울 강남구 포이동 일원", "lat": 37.4727, "lng": 127.0456, "status": "개발 예정 (신설)"},
            {"name": "구룡역", "address": "서울 강남구 개포동 일원", "lat": 37.487023, "lng": 127.059002, "status": "기존"},
            {"name": "도곡역", "address": "서울 강남구 도곡동 일원", "lat": 37.490559, "lng": 127.055112, "status": "기존"},
            {"name": "수서역", "address": "서울 강남구 수서동 일원", "lat": 37.488258, "lng": 127.100580, "status": "기존"},
            {"name": "복정역", "address": "서울 송파구 장지동 일원", "lat": 37.470747, "lng": 127.126730, "status": "기존"},
            {"name": "위례중앙역", "address": "서울 송파구 위례신도시 일원", "lat": 37.474786, "lng": 127.142215, "status": "개발 예정 (신설)"}
        ]

        for s in wirye_gwacheon_stations:
            cursor.execute(
                "INSERT INTO subways (line, name, address, lat, lng, status) VALUES (?, ?, ?, ?, ?, ?)",
                ("위례과천선", s["name"], s["address"], s["lat"], s["lng"], s["status"])
            )
            count += 1

        conn.commit()
        conn.close()
        print("Successfully loaded '위례과천선' stations!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
