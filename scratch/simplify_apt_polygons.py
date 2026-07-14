import geopandas as gpd
import time
import os

in_path = 'c:/Users/llll/Documents/두인경매/바이브코딩/public/data/apt_info_500_polygons.geojson'
out_path = 'c:/Users/llll/Documents/두인경매/바이브코딩/public/data/apt_info_500_polygons.geojson' # overwrite

print(f"Loading {in_path} (size: {os.path.getsize(in_path) / 1024 / 1024:.2f} MB)")
start = time.time()
gdf = gpd.read_file(in_path)

print("Simplifying geometry...")
# Simplify: tolerance 0.0001 degrees is ~11 meters.
# 0.00005 degrees is ~5.5 meters, which is very safe for keeping the parcel shape.
gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.00005, preserve_topology=True)

print("Saving...")
gdf.to_file(out_path, driver='GeoJSON')
end = time.time()
print(f"Done in {end - start:.2f} seconds. New size: {os.path.getsize(out_path) / 1024 / 1024:.2f} MB")
