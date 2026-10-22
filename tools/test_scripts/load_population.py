import os
import sqlite3
import pandas as pd
from pyproj import Transformer

print("Starting population data load...")

db_path = 'data/map_data.db'
csv_path = 'data/서울특별시 250M격자 생활인구(내국인).csv'

if not os.path.exists(csv_path):
    print(f"Error: {csv_path} not found.")
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

def grid_to_xy(grid_code):
    if len(grid_code) != 10:
        return None, None
    x_char = grid_code[0]
    y_char = grid_code[1]
    
    if x_char not in X_PREFIX or y_char not in Y_PREFIX:
        return None, None
        
    x_val = grid_code[2:6]
    y_val = grid_code[6:10]
    
    try:
        x_m = X_PREFIX[x_char] * 100000 + int(x_val) * 10
        y_m = Y_PREFIX[y_char] * 100000 + int(y_val) * 10
        return x_m, y_m
    except:
        return None, None

print("Loading CSV...")
df = pd.read_csv(csv_path, encoding='cp949', usecols=[3, 4])
df.columns = ['grid_code', 'population']

print(f"Loaded {len(df)} rows. Cleaning data...")
# Some population values might be '*'
df['population'] = pd.to_numeric(df['population'], errors='coerce').fillna(0)

print("Grouping by grid code...")
grouped = df.groupby('grid_code')['population'].mean().reset_index()
print(f"Unique grids: {len(grouped)}")

transformer = Transformer.from_crs("epsg:5179", "epsg:4326", always_xy=True)

print("Connecting to DB and creating table...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS population_grids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grid_code TEXT UNIQUE,
    lat REAL,
    lng REAL,
    avg_population REAL
)
''')

# Clear existing data just in case
cursor.execute('DELETE FROM population_grids')

print("Inserting data into database...")
records = []
for _, row in grouped.iterrows():
    grid_code = row['grid_code']
    pop = row['population']
    
    x, y = grid_to_xy(grid_code)
    if x is not None and y is not None:
        lng, lat = transformer.transform(x, y)
        records.append((grid_code, lat, lng, pop))

cursor.executemany('''
INSERT INTO population_grids (grid_code, lat, lng, avg_population)
VALUES (?, ?, ?, ?)
''', records)

conn.commit()
conn.close()

print(f"Successfully inserted {len(records)} records into population_grids.")
