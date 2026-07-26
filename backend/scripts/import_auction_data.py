import pandas as pd
import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/map_data.db')

def get_latest_excel_path():
    base_data_dir = os.path.join(os.path.dirname(__file__), '../../data')
    if not os.path.exists(base_data_dir):
        base_data_dir = 'data'
    
    search_dirs = [
        base_data_dir,
        os.path.join(base_data_dir, '경공매업데이트')
    ]
    
    excel_files = []
    for d in search_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.startswith('경공매데이터') and f.endswith('.xlsx'):
                    path = os.path.join(d, f)
                    excel_files.append((os.path.getmtime(path), path))
                    
    if excel_files:
        excel_files.sort(reverse=True)
        # Log the selected path for visibility
        print(f"Detected latest Excel file: {excel_files[0][1]}")
        return excel_files[0][1]
            
    return os.path.join(base_data_dir, '경공매데이터_260515.xlsx')

import sys
EXCEL_PATH = sys.argv[1] if len(sys.argv) > 1 else get_latest_excel_path()


def import_auctions():
    print("Connecting to DB...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS auctions')
    cursor.execute('''
        CREATE TABLE auctions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_no TEXT,
            sale_type TEXT,
            property_type TEXT,
            address TEXT,
            appraisal_price REAL,
            min_price REAL,
            min_bid_rate REAL,
            lat REAL,
            lng REAL,
            area_size REAL,
            subway_dist REAL,
            univ_dist REAL,
            ind_dist REAL,
            elite_school TEXT,
            households INTEGER,
            land_size REAL,
            min_price_per_pyeong REAL,
            special_notes TEXT,
            official_land_price REAL,
            sale_date TEXT
        )
    ''')
    cursor.execute('DELETE FROM auctions')
    
    print("Reading Excel file...")
    # Find the header row by looking for '사건번호'
    df = pd.read_excel(EXCEL_PATH, header=0) 
    if '사건번호' not in df.columns:
        df = pd.read_excel(EXCEL_PATH, header=1)
    if '사건번호' not in df.columns:
        df = pd.read_excel(EXCEL_PATH, header=2)

    print(f"Loaded {len(df)} rows. Columns: {df.columns.tolist()[:10]}...")
    
    count = 0
    for idx, row in df.iterrows():
        try:
            lat = float(row.get('위도', 0))
            lng = float(row.get('경도', 0))
            
            # Allow strings that look like numbers
            if pd.isna(lat) or pd.isna(lng) or lat == 0:
                continue
                
            case_no = str(row.get('사건번호', '')).strip()
            if not case_no or case_no == 'nan':
                continue
                
            sale_type = str(row.get('구분', '')).strip() # 경매 or 공매
            
            # Use Column W '형태' as the primary property type classification
            property_type = str(row.get('형태', '')).strip()
            if not property_type or property_type == 'nan' or property_type == '대분류없음':
                property_type = str(row.get('종류', '')).strip()
                
            address = str(row.get('주소', '')).strip()
            
            # Handle string prices like "1,000,000"
            try:
                appraisal_str = str(row.get('감정가(M)', '0')).replace(',', '').strip()
                min_price_str = str(row.get('최저가(M)', '0')).replace(',', '').strip()
                appraisal_price = float(appraisal_str) if appraisal_str else 0
                min_price = float(min_price_str) if min_price_str else 0
            except ValueError:
                appraisal_price = 0
                min_price = 0
                
            if appraisal_price > 0:
                min_bid_rate = round((min_price / appraisal_price) * 100, 1)
            else:
                min_bid_rate = 0
                
            # New columns
            area_size = float(row.get('전용면적(평)', 0)) if not pd.isna(row.get('전용면적(평)', 0)) else 0
            subway_dist = float(row.get('역거리', 0)) if not pd.isna(row.get('역거리', 0)) else 0
            univ_dist = float(row.get('대학거리', 0)) if not pd.isna(row.get('대학거리', 0)) else 0
            ind_dist = float(row.get('산단거리', 0)) if not pd.isna(row.get('산단거리', 0)) else 0
            elite_school = str(row.get('학군', '')).strip()
            
            try:
                households = int(row.get('세대수', 0)) if not pd.isna(row.get('세대수', 0)) else 0
            except ValueError:
                households = 0

            try:
                land_size_str = str(row.get('대지권(평)', '0')).replace(',', '').strip()
                land_size = float(land_size_str) if land_size_str and land_size_str != 'nan' else 0
            except ValueError:
                land_size = 0
                
            try:
                mppp_str = str(row.get('평당최저가격', '0')).replace(',', '').strip()
                min_price_per_pyeong = float(mppp_str) if mppp_str and mppp_str != 'nan' else 0
            except ValueError:
                min_price_per_pyeong = 0
            
            # special notes
            notes = [
                str(row.get('특이사항', '')),
                str(row.get('특이사항1', '')),
                str(row.get('특이코드', '')),
                str(row.get('HUG포기', ''))
            ]
            special_notes = " ".join([n for n in notes if n != 'nan' and n.strip()])

            # official land price (시가표준액)
            try:
                olp_str = str(row.get('시가표준액', '0')).replace(',', '').strip()
                official_land_price = float(olp_str) if olp_str and olp_str != 'nan' else 0
            except ValueError:
                official_land_price = 0
            
            # sale date (입찰일)
            sale_date_val = row.get('입찰일')
            sale_date = ""
            if pd.notna(sale_date_val) and str(sale_date_val).strip() not in ['0', '0.0', 'nan', '']:
                if isinstance(sale_date_val, datetime.datetime):
                    sale_date = sale_date_val.strftime('%Y-%m-%d')
                else:
                    try:
                        dt = pd.to_datetime(sale_date_val)
                        if pd.notna(dt) and dt.year > 1970:
                            sale_date = dt.strftime('%Y-%m-%d')
                    except Exception:
                        sale_date = str(sale_date_val).strip()
            
            cursor.execute('''
                INSERT INTO auctions (case_no, sale_type, property_type, address, appraisal_price, min_price, min_bid_rate, lat, lng, area_size, subway_dist, univ_dist, ind_dist, elite_school, households, land_size, min_price_per_pyeong, special_notes, official_land_price, sale_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (case_no, sale_type, property_type, address, appraisal_price, min_price, min_bid_rate, lat, lng, area_size, subway_dist, univ_dist, ind_dist, elite_school, households, land_size, min_price_per_pyeong, special_notes, official_land_price, sale_date))
            count += 1
            
        except Exception as e:
            if count == 0:
                print(f"Error on first failed row: {e}")
            # Skip rows with errors
            pass
            
    conn.commit()
    conn.close()
    print(f"Successfully inserted {count} auction properties into DB.")

if __name__ == '__main__':
    import_auctions()
