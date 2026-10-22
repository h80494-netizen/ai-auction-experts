import os
import sqlite3
import pandas as pd
import glob
from pyproj import Transformer
from collections import defaultdict

print("Starting 500m population data load...")

db_path = 'data/map_data.db'
csv_dir = 'data/500격자주거직장인구'

if not os.path.exists(csv_dir):
    print(f"Error: {csv_dir} not found.")
    exit(1)

# X, Y prefix mapping for National Grid Code (UTM-K based)
X_PREFIX = {
    '가': 7, '나': 8, '다': 9, '라': 10, 
    '마': 11, '바': 12, '사': 13, '아': 14
}
Y_PREFIX = {
    '가': 13, '나': 14, '다': 15, '라': 16, 
    '마': 17, '바': 18, '사': 19, '아': 20, 
    '자': 21, '차': 22
}

def grid_to_xy_500m(grid_code):
    if len(grid_code) != 8:
        return None, None
    x_char = grid_code[0]
    y_char = grid_code[1]
    
    if x_char not in X_PREFIX or y_char not in Y_PREFIX:
        return None, None
        
    x_val = grid_code[2:4]
    x_suf = grid_code[4]
    y_val = grid_code[5:7]
    y_suf = grid_code[7]
    
    try:
        x_m = X_PREFIX[x_char] * 100000 + int(x_val) * 1000 + (500 if x_suf == 'b' else 0)
        y_m = Y_PREFIX[y_char] * 100000 + int(y_val) * 1000 + (500 if y_suf == 'b' else 0)
        return x_m, y_m
    except:
        return None, None

transformer = Transformer.from_crs("epsg:5179", "epsg:4326", always_xy=True)

# grid_code -> {'residential': 0, 'worker': 0}
grid_data = defaultdict(lambda: {'residential': 0, 'worker': 0})

print("Parsing CSVs...")
files = glob.glob(os.path.join(csv_dir, '*.csv'))
for f in files:
    print(f"Reading {os.path.basename(f)}...")
    df = pd.read_csv(f, encoding='cp949', header=None)
    
    # 0: Year, 1: GridCode, 2: Category, 3: Value
    for _, row in df.iterrows():
        code = str(row[1])
        cat = str(row[2])
        try:
            val = float(row[3])
        except:
            val = 0.0
            
        if cat == 'to_in_001':
            grid_data[code]['residential'] += val
        elif cat == 'to_em_020':
            grid_data[code]['worker'] += val

print(f"Total unique grids extracted: {len(grid_data)}")

print("Connecting to DB and creating table...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS population_500m_grids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grid_code TEXT UNIQUE,
    lat REAL,
    lng REAL,
    residential_pop REAL,
    worker_pop REAL
)
''')

# Clear existing data just in case
cursor.execute('DELETE FROM population_500m_grids')

print("Transforming coordinates and preparing insert...")
records = []
for grid_code, data in grid_data.items():
    res = data['residential']
    work = data['worker']
    
    x, y = grid_to_xy_500m(grid_code)
    if x is not None and y is not None:
        lng, lat = transformer.transform(x, y)
        records.append((grid_code, lat, lng, res, work))

print(f"Inserting {len(records)} records into population_500m_grids...")
cursor.executemany('''
INSERT INTO population_500m_grids (grid_code, lat, lng, residential_pop, worker_pop)
VALUES (?, ?, ?, ?, ?)
''', records)

# Create index for fast spatial queries
cursor.execute('CREATE INDEX IF NOT EXISTS idx_population_500m_grids_lat_lng ON population_500m_grids(lat, lng)')

conn.commit()
conn.close()

print("Successfully loaded 500m population grids.")
