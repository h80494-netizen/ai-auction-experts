import geopandas as gpd
import glob
import os

shp_files = glob.glob('*.shp')
seoul_shp = next((f for f in shp_files if os.path.getsize(f) > 3000000), None)

print("Reading shapefile with utf-8 encoding...")
gdf = gpd.read_file(seoul_shp, encoding='utf-8', engine='pyogrio')

print("Converting to epsg:4326...")
gdf = gdf.to_crs(epsg=4326)

print("Exporting to GeoJSON...")
gdf.to_file('public/data/seoul_commercial.geojson', driver='GeoJSON', encoding='utf-8')
print("Done!")
