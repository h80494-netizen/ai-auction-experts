import os
import zipfile
import tempfile
import glob
import geopandas as gpd
import pandas as pd

def extract_and_load(zip_patterns, data_dir, temp_dir):
    """
    Extracts shapefiles from zips matching zip_patterns and loads them into a list of GeoDataFrames.
    Returns concatenated GeoDataFrame.
    """
    zip_files = []
    for pattern in zip_patterns:
        zip_files.extend(glob.glob(os.path.join(data_dir, pattern)))
        
    gdfs = []
    
    for zip_path in zip_files:
        print(f"Processing {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
        shp_files = glob.glob(os.path.join(temp_dir, '*.shp'))
        if not shp_files:
            continue
            
        shp_file = shp_files[0]
        # Read shapefile
        gdf = gpd.read_file(shp_file, encoding='cp949')
        if gdf.crs is None:
            gdf.set_crs(epsg=5179, inplace=True)
            
        # Standardize columns: keep 'gid' and 'val'
        if 'val' in gdf.columns and 'gid' in gdf.columns:
            gdf = gdf[['gid', 'val', 'geometry']]
            gdfs.append(gdf)
        
        # Clean up
        for f in glob.glob(os.path.join(temp_dir, '*')):
            os.remove(f)
            
    if gdfs:
        return pd.concat(gdfs, ignore_index=True).drop_duplicates(subset=['gid'])
    return gpd.GeoDataFrame()

def process_data():
    data_dir = 'data'
    output_dir = 'public/data'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'old_buildings_ratio.geojson')
    
    old_patterns = [
        '*(B100)국토통계_건축물-시기별 건축물 수(35년 이상)-(격자)*.zip'
    ]
    total_patterns = [
        '*(B100)국토통계_건축물-건축물 수 합계 통계-(격자)*.zip',
        '서울건축물수.zip'
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print("Loading 35+ year buildings data...")
        old_gdf = extract_and_load(old_patterns, data_dir, temp_dir)
        
        print("Loading total buildings data...")
        total_gdf = extract_and_load(total_patterns, data_dir, temp_dir)
        
    if old_gdf.empty or total_gdf.empty:
        print("Failed to load required data.")
        return
        
    print("Merging data on 'gid'...")
    # Drop geometry from total_gdf for merging
    total_df = total_gdf.drop(columns=['geometry']).rename(columns={'val': 'total_val'})
    
    merged_gdf = old_gdf.merge(total_df, on='gid', how='inner')
    
    # Calculate ratio
    merged_gdf['ratio'] = merged_gdf['val'] / merged_gdf['total_val']
    
    # Filter where (ratio >= 0.6 and total_val >= 500) OR (val >= 1000)
    filtered_gdf = merged_gdf[((merged_gdf['total_val'] >= 500) & (merged_gdf['ratio'] >= 0.6)) | (merged_gdf['val'] >= 1000)].copy()
    
    print(f"Found {len(filtered_gdf)} grids matching old building criteria.")
    
    if filtered_gdf.empty:
        print("No grids found matching the criteria.")
        return
        
    print("Reprojecting to EPSG:4326...")
    filtered_gdf = filtered_gdf.to_crs(epsg=4326)
    
    # Keep necessary columns
    filtered_gdf['ratio_pct'] = (filtered_gdf['ratio'] * 100).round(1)
    final_gdf = filtered_gdf[['gid', 'val', 'total_val', 'ratio_pct', 'geometry']]
    
    print("Saving to GeoJSON...")
    final_gdf.to_file(output_file, driver='GeoJSON')
    print(f"Successfully saved to {output_file}")

if __name__ == '__main__':
    process_data()
