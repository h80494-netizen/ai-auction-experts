import geopandas as gpd
import os

data_dir = r"c:\Users\llll\Documents\두인경매\바이브코딩\data"

zips = [
    ("UQ111_용도지역(도시지역)_202602.zip", "zip://data/UQ111_용도지역(도시지역)_202602.zip!shp파일"),
    ("UQ120_도시계획사업(서울플랜+)_202602 (1).zip", "zip://data/UQ120_도시계획사업(서울플랜+)_202602 (1).zip!945_UQ120_도시계획사업(서울플랜+)_202602/shp파일")
]

for file_name, zip_uri in zips:
    try:
        print(f"\n=========================================")
        print(f"Reading shapefile schema from: {file_name}")
        gdf = gpd.read_file(zip_uri)
        print(f"CRS: {gdf.crs}")
        print("Columns:", list(gdf.columns))
        print("First 3 rows:")
        print(gdf.head(3))
    except Exception as e:
        print(f"Error reading shapefile from {file_name}: {e}")
