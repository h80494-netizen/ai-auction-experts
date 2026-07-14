import geopandas as gpd

# Redevelopment
try:
    zip_uq120 = "zip://data/UQ120_도시계획사업(서울플랜+)_202602 (1).zip!945_UQ120_도시계획사업(서울플랜+)_202602/shp파일"
    gdf_dev = gpd.read_file(zip_uq120, encoding='cp949')
    print("Redevelopment first 5 names (CP949):")
    print(gdf_dev['DGM_NM'].head() if 'DGM_NM' in gdf_dev.columns else "No DGM_NM")
except Exception as e:
    print("CP949 error dev:", e)

# Zoning
try:
    zip_uq111 = "zip://data/UQ111_용도지역(도시지역)_202602.zip!shp파일"
    gdf_zone = gpd.read_file(zip_uq111, encoding='cp949')
    print("Zoning first 5 names (CP949):")
    print(gdf_zone['DGM_NM'].head() if 'DGM_NM' in gdf_zone.columns else "No DGM_NM")
except Exception as e:
    print("CP949 error zone:", e)
