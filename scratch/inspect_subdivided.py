import geopandas as gpd

gdf = gpd.read_file("public/data/old_buildings_ratio.geojson")
print("Row count:", len(gdf))
print("Resolution property:", gdf['resolution'].unique())
print("Columns:", gdf['resolution'].unique())
print("Columns:", gdf.columns)
print("Describe total_val:")
print(gdf['total_val'].describe())
print("Max total_val:", gdf['total_val'].max())
print("Any row where total_val < 250:", (gdf['total_val'] < 250).sum())
print("Head:")
print(gdf.head())
