import geopandas as gpd

zip_uq111 = "zip://data/UQ111_용도지역(도시지역)_202602.zip!shp파일"

for enc in ['utf-8', 'euc-kr', 'cp949', 'iso-8859-1']:
    try:
        gdf = gpd.read_file(zip_uq111, encoding=enc)
        print(f"\n--- Encoding: {enc} ---")
        print(gdf['DGM_NM'].head())
    except Exception as e:
        print(f"Error {enc}: {e}")
