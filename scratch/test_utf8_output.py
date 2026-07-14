import geopandas as gpd

zip_uq111 = "zip://data/UQ111_용도지역(도시지역)_202602.zip!shp파일"
gdf = gpd.read_file(zip_uq111, encoding='cp949')

with open("scratch/encoding_out.txt", "w", encoding="utf-8") as f:
    for i, name in enumerate(gdf['DGM_NM'].head(20)):
        f.write(f"{i}: {repr(name)} -> {name}\n")

print("Wrote head to scratch/encoding_out.txt")
