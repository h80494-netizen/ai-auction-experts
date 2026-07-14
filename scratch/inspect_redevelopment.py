import geopandas as gpd

zip_path = 'zip://data/UQ120_도시계획사업(서울플랜+)_202602 (1).zip!945_UQ120_도시계획사업(서울플랜+)_202602/shp파일'
gdf = gpd.read_file(zip_path, encoding='cp949')

output_file = 'scratch/redevelopment_names.txt'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"Columns: {list(gdf.columns)}\n\n")
    f.write("Sample rows:\n")
    cols_to_print = [c for c in gdf.columns if c != 'geometry']
    f.write(gdf[cols_to_print].head(50).to_string())
    f.write("\n\nUnique values in DGM_NM:\n")
    f.write(gdf['DGM_NM'].value_counts().head(50).to_string())
