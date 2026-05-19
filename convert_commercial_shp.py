import geopandas as gpd
import json
import os

# Load the shapefile
shp_path = '서울상권.shp'
try:
    gdf = gpd.read_file(shp_path, engine='fiona', encoding='utf-8')
except Exception as e:
    gdf = gpd.read_file(shp_path, engine='fiona', encoding='cp949')

print("Columns:", gdf.columns)
print("CRS:", gdf.crs)
print("Head:", gdf.head(1))

# Reproject to WGS84
if gdf.crs is not None:
    gdf = gdf.to_crs(epsg=4326)
else:
    # If no CRS is defined, it might be EPSG:5181 (Seoul standard)
    gdf.set_crs(epsg=5181, inplace=True)
    gdf = gdf.to_crs(epsg=4326)

# Save to geojson
out_path = os.path.join('public', 'data', 'seoul_commercial.geojson')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
gdf.to_file(out_path, driver='GeoJSON', encoding='utf-8')
print(f"Saved to {out_path}")
