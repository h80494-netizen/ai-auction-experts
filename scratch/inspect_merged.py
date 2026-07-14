import os
import zipfile
import tempfile
import glob
import geopandas as gpd
import pandas as pd

def extract_and_load(zip_patterns, data_dir, temp_dir):
    zip_files = []
    for pattern in zip_patterns:
        zip_files.extend(glob.glob(os.path.join(data_dir, pattern)))
    gdfs = []
    for zip_path in zip_files:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        shp_files = glob.glob(os.path.join(temp_dir, '*.shp'))
        if not shp_files:
            continue
        shp_file = shp_files[0]
        gdf = gpd.read_file(shp_file, encoding='cp949')
        if gdf.crs is None:
            gdf.set_crs(epsg=5179, inplace=True)
        if 'val' in gdf.columns and 'gid' in gdf.columns:
            gdf = gdf[['gid', 'val', 'geometry']]
            gdfs.append(gdf)
        for f in glob.glob(os.path.join(temp_dir, '*')):
            os.remove(f)
    if gdfs:
        return pd.concat(gdfs, ignore_index=True).drop_duplicates(subset=['gid'])
    return gpd.GeoDataFrame()

def main():
    data_dir = 'data'
    old_patterns = ['*(B100)국토통계_건축물-시기별 건축물 수(35년 이상)-(격자)*.zip']
    total_patterns = ['*(B100)국토통계_건축물-건축물 수 합계 통계-(격자)*.zip', '서울건축물수.zip']
    
    with tempfile.TemporaryDirectory() as temp_dir:
        old_gdf = extract_and_load(old_patterns, data_dir, temp_dir)
        total_gdf = extract_and_load(total_patterns, data_dir, temp_dir)
        
    total_df = total_gdf.drop(columns=['geometry']).rename(columns={'val': 'total_val'})
    merged = old_gdf.merge(total_df, on='gid', how='inner')
    merged['ratio'] = merged['val'] / merged['total_val']
    
    print("Merged shape:", merged.shape)
    print("Null total_val count:", merged['total_val'].isnull().sum())
    print("Describe total_val in merged:")
    print(merged['total_val'].describe())
    print("Max total_val in merged:", merged['total_val'].max())
    
if __name__ == '__main__':
    main()
