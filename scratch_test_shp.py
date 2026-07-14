import geopandas as gpd

zip_uq120 = "zip://data/UQ120_도시계획사업(서울플랜+)_202602 (1).zip!945_UQ120_도시계획사업(서울플랜+)_202602/shp파일"
gdf = gpd.read_file(zip_uq120, encoding='cp949')

print("Columns in UQ120:")
print(gdf.columns.tolist())
print("\nFirst 5 rows:")
print(gdf[['DGM_NM', 'PROPEL_CD']].head(10))
print("\nUnique PROPEL_CD values:")
print(gdf['PROPEL_CD'].value_counts())
