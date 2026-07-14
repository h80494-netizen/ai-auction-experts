import geopandas as gpd
import pandas as pd
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

files = [
    'data/지구경계_서울_20260430_5186.zip',
    'data/지구경계_경기_20260430_5186.zip',
    'data/지구경계_인천_20260430_5186.zip'
]

for f in files:
    try:
        print(f"\n--- Inspecting {f} ---")
        gdf = gpd.read_file(f'zip://{f}')
        print("Columns:", gdf.columns.tolist())
        if 'stepCode' in gdf.columns:
            print("Unique stepCode values:")
            print(gdf['stepCode'].value_counts())
        else:
            print("stepCode NOT in columns!")
    except Exception as e:
        print(f"Error inspecting {f}: {e}")
