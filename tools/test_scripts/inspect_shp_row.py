import geopandas as gpd
gdf = gpd.read_file('data/서울공시지가.shp', nrows=1)
print(gdf.iloc[0])
