# -*- coding: utf-8 -*-
import geopandas as gpd
import os

shp_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\gris_shp\Gyeonggi_Jeongbi_Guyeok.shp"
if not os.path.exists(shp_path):
    print("Shapefile does not exist at:", shp_path)
    exit(1)

print("Loading shapefile...")
gdf = gpd.read_file(shp_path, encoding='cp949')
print("Columns:", gdf.columns)
print("Shape:", gdf.shape)
print("CRS:", gdf.crs)
print("\nFirst 10 rows:")
for idx, row in gdf.head(10).iterrows():
    print(f"Row {idx}:")
    for col in gdf.columns:
        if col != 'geometry':
            print(f"  {col}: {row[col]}")
        else:
            print(f"  geometry type: {row['geometry'].geom_type}")
