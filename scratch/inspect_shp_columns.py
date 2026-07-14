import geopandas as gpd

try:
    gdf = gpd.read_file('zip://data/지구경계_서울_20260430_5186.zip')
    print("Columns:", gdf.columns)
    print("Shape:", gdf.shape)
    print("First 5 rows:")
    print(gdf.head())
    print("Coordinate Reference System (CRS):", gdf.crs)
except Exception as e:
    print("Error reading zip shp:", e)
