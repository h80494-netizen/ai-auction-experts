import geopandas as gpd
import os

shp_path = 'data/산업단지/산업단지.shp'
print("File exists:", os.path.exists(shp_path))

gdf = gpd.read_file(shp_path)
print("Columns:", gdf.columns)
print("Head:\n", gdf.head())
print("Geom type:", gdf.geom_type.head())
print("CRS:", gdf.crs)
print("Total rows:", len(gdf))
