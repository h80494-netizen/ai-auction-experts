import pandas as pd
import sqlite3
from pyproj import Transformer
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir, 'data', '서울특별시 250M격자 생활인구(내국인).csv')
db_path = os.path.join(base_dir, 'backend', 'data', 'map_data.db')

print("Reading CSV data...")
df = pd.read_csv(csv_path, encoding='euc-kr')

# Clean '*' characters and convert to float
df['생활인구합계'] = df['생활인구합계'].replace('*', 0).astype(float)

# Group by grid and calculate mean (daily average)
print("Aggregating daily average...")
agg_df = df.groupby('250m격자')['생활인구합계'].mean().reset_index()

# EPSG:5179 to EPSG:4326
transformer = Transformer.from_crs('EPSG:5179', 'EPSG:4326', always_xy=True)

def parse_grid_to_latlng(grid_str):
    try:
        if not isinstance(grid_str, str) or len(grid_str) < 10:
            return None, None
            
        x_char = grid_str[0]
        y_char = grid_str[1]
        x_num = int(grid_str[2:6])
        y_num = int(grid_str[6:10])
        
        chars = ['가', '나', '다', '라', '마', '바', '사', '아', '자', '차', '카', '타', '파', '하']
        
        x_idx = chars.index(x_char)
        y_idx = chars.index(y_char)
        
        x_base = 700000 + x_idx * 100000
        y_base = 1300000 + y_idx * 100000
        
        # Grid center point (+125m)
        x_m = x_base + (x_num * 10) + 125
        y_m = y_base + (y_num * 10) + 125
        
        lon, lat = transformer.transform(x_m, y_m)
        return lat, lon
    except Exception as e:
        return None, None

print("Converting coordinates...")
coords = agg_df['250m격자'].apply(parse_grid_to_latlng)
agg_df['lat'] = [c[0] for c in coords]
agg_df['lng'] = [c[1] for c in coords]

agg_df = agg_df.dropna(subset=['lat', 'lng'])
print(f"Total grids processed: {len(agg_df)}")

print("Saving to database...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS population_grids (
    grid_id TEXT PRIMARY KEY,
    lat REAL,
    lng REAL,
    avg_population REAL
)
''')
cursor.execute('DELETE FROM population_grids')

insert_query = '''
INSERT INTO population_grids (grid_id, lat, lng, avg_population)
VALUES (?, ?, ?, ?)
'''
data_tuples = list(agg_df[['250m격자', 'lat', 'lng', '생활인구합계']].itertuples(index=False, name=None))
cursor.executemany(insert_query, data_tuples)

cursor.execute('CREATE INDEX IF NOT EXISTS idx_pop_lat ON population_grids(lat)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_pop_lng ON population_grids(lng)')

conn.commit()
conn.close()

print("Success! Data loaded into population_grids table.")
