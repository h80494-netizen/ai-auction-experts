import os
import geopandas as gpd

shp_path = 'c:/Users/llll/Documents/두인경매/바이브코딩/data/예정도로.shp'
out_dir = 'c:/Users/llll/Documents/두인경매/바이브코딩/public/data'
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'planned_roads_100m.geojson')

print(f"Loading {shp_path}...")
try:
    gdf = gpd.read_file(shp_path, encoding='euc-kr') # Usually shapefiles from Korea are euc-kr or cp949
except Exception as e:
    print("Trying utf-8 encoding due to error:", e)
    gdf = gpd.read_file(shp_path, encoding='utf-8')

print("Original CRS:", gdf.crs)
if not gdf.crs:
    print("Warning: CRS is None. Assuming EPSG:4326 for now.")
    gdf = gdf.set_crs(epsg=4326)

# Reproject to EPSG:5179 (Korea TM) to buffer in meters
print("Reprojecting to EPSG:5179 for buffering...")
gdf_meter = gdf.to_crs(epsg=5179)

print("Applying 100m buffer...")
gdf_meter['geometry'] = gdf_meter['geometry'].buffer(100)

print("Reprojecting back to EPSG:4326...")
gdf_final = gdf_meter.to_crs(epsg=4326)

print(f"Saving to {out_path}...")
# Convert to geojson
gdf_final.to_file(out_path, driver='GeoJSON', encoding='utf-8')

print("Successfully processed planned roads.")
