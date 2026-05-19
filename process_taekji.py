import geopandas as gpd
import pandas as pd

# Files to process
files = [
    'data/지구경계_서울_20260430_5186.zip',
    'data/지구경계_경기_20260430_5186.zip',
    'data/지구경계_인천_20260430_5186.zip'
]

gdfs = []
for f in files:
    gdf = gpd.read_file(f'zip://{f}')
    gdf = gdf.to_crs('EPSG:4326')
    gdfs.append(gdf)

merged = pd.concat(gdfs, ignore_index=True)
merged.to_file('public/data/taekji.geojson', driver='GeoJSON')
print('Successfully saved taekji.geojson')
