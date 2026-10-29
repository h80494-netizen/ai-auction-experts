import pandas as pd
import sqlite3
import os
from pyproj import Transformer

def import_commercial_areas():
    csv_path = os.path.join(os.path.dirname(__file__), '../../data/서울시상권.csv')
    db_path = os.path.join(os.path.dirname(__file__), '../data/map_data.db')
    
    print(f"Reading CSV from {csv_path}")
    # Read the CSV with correct encoding, ignoring bad lines if any
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding='cp949')
        
    print(f"Loaded {len(df)} rows.")
    
    # Coordinate transformer from EPSG:5181 to EPSG:4326 (WGS84)
    # 5181 parameters
    transformer = Transformer.from_crs("EPSG:5181", "EPSG:4326", always_xy=True)
    
    # Extract relevant columns
    # Based on preview: 
    # TRDAR_SE_C, TRDAR_SE_1 (분류), TRDAR_CD_N (상권명), XCNTS_VALU, YDNTS_VALU
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS commercial_areas')
    cursor.execute('''
        CREATE TABLE commercial_areas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name TEXT,
            lat REAL,
            lng REAL,
            population INTEGER
        )
    ''')
    
    count = 0
    for idx, row in df.iterrows():
        try:
            x = float(row.get('XCNTS_VALU', 0))
            y = float(row.get('YDNTS_VALU', 0))
            
            if pd.isna(x) or pd.isna(y) or x == 0 or y == 0:
                continue
                
            lng, lat = transformer.transform(x, y)
            
            category = str(row.get('TRDAR_SE_1', '')).strip()
            name = str(row.get('TRDAR_CD_N', '')).strip()
            
            # Find population column (typically index 15 or containing '총_유동인구_수')
            population = 0
            pop_cols = [c for c in df.columns if '총_유동인구_수' in c or '총유동인구수' in c]
            if pop_cols:
                try:
                    population = int(row[pop_cols[0]])
                except:
                    population = 0
            else:
                # Fallback to column index 15 if name matching fails due to encoding
                try:
                    population = int(row.iloc[15])
                except:
                    pass
            
            # If the header names are different (e.g. translated)
            if not name:
                # try alternative names based on preview:
                name_cols = [c for c in df.columns if '상권_코드_명' in c or '상권명' in c]
                if name_cols:
                    name = str(row[name_cols[0]]).strip()
                    
            if not category:
                cat_cols = [c for c in df.columns if '상권_구분_코드_명' in c or '구분' in c]
                if cat_cols:
                    category = str(row[cat_cols[0]]).strip()
                    
            cursor.execute('''
                INSERT INTO commercial_areas (category, name, lat, lng, population)
                VALUES (?, ?, ?, ?, ?)
            ''', (category, name, lat, lng, population))
            count += 1
            
        except Exception as e:
            if count == 0:
                print(f"Error on first row: {e}")
            pass
            
    conn.commit()
    conn.close()
    print(f"Successfully inserted {count} commercial areas into DB.")

if __name__ == '__main__':
    import_commercial_areas()
