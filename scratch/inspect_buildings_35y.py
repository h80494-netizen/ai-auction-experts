import geopandas as gpd
import os

shp_path = "data/buildings_35y/vl_blk.shp"
if os.path.exists(shp_path):
    print("Reading shapefile...")
    gdf = gpd.read_file(shp_path)
    with open("scratch/inspect_buildings_35y_output.txt", "w", encoding="utf-8") as f:
        f.write(f"CRS: {gdf.crs}\n")
        f.write(f"Columns: {gdf.columns.tolist()}\n")
        f.write(f"Row count: {len(gdf)}\n")
        f.write("Head:\n")
        f.write(gdf[['gid', 'lbl', 'val']].head().to_string())
        f.write("\nGeometry head:\n")
        f.write(gdf['geometry'].head().to_string())
    print("Done inspection, output written to scratch/inspect_buildings_35y_output.txt")
else:
    print(f"File {shp_path} not found.")
