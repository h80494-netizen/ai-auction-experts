import geopandas as gpd

shp_files = [
    'data/서울공시지가.shp',
    'data/경기공시지가.shp',
    'data/인천공시지가.shp'
]

for file in shp_files:
    print(f"\n--- Reading {file} ---")
    try:
        gdf = gpd.read_file(file, nrows=5)
        print("Columns:", gdf.columns.tolist())
        print("CRS:", gdf.crs)
        print(gdf.head())
    except Exception as e:
        print("Error:", e)
