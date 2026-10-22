import os
import zipfile
import tempfile
import glob
import geopandas as gpd
import pandas as pd
import argparse
from shapely.geometry import Polygon

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

def subdivide_to_250m(gdf, threshold_val_250m):
    """
    Subdivides 1km grid cells into 16 smaller 250m cells.
    Distributes total_val and val uniformly (divided by 16) and filters.
    """
    print(f"Simulating 250m subdivision from 1km data (threshold: {threshold_val_250m}+ total buildings)...")
    sub_records = []
    
    # Drop rows with NaN values to prevent NaN comparisons
    gdf = gdf.dropna(subset=['val', 'total_val', 'ratio']).copy()
    
    # Ensure correct CRS for metric coordinates
    if gdf.crs != 'EPSG:5179':
        gdf = gdf.to_crs(epsg=5179)
        
    for idx, row in gdf.iterrows():
        geom = row['geometry']
        if geom.geom_type != 'Polygon':
            continue
            
        minx, miny, maxx, maxy = geom.bounds
        # A 1km grid is 1000m x 1000m. Let's create a 4x4 grid of 250m cells
        for i in range(4):
            for j in range(4):
                total_sub = row['total_val'] / 16.0
                if total_sub < threshold_val_250m:
                    continue
                    
                ratio_sub = row['ratio']
                if ratio_sub < 0.6 or ratio_sub > 1.0:
                    continue
                    
                val_sub = row['val'] / 16.0
                
                x1 = minx + i * 250
                y1 = miny + j * 250
                x2 = x1 + 250
                y2 = y1 + 250
                
                sub_poly = Polygon([(x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1)])
                
                sub_records.append({
                    'gid': f"{row['gid']}_{i}_{j}",
                    'val': val_sub,
                    'total_val': total_sub,
                    'ratio': ratio_sub,
                    'geometry': sub_poly
                })
                
    if not sub_records:
        return gpd.GeoDataFrame(columns=['gid', 'val', 'total_val', 'ratio', 'geometry'], crs='EPSG:5179')
        
    sub_gdf = gpd.GeoDataFrame(sub_records, crs='EPSG:5179')
    return sub_gdf

def process_data():
    parser = argparse.ArgumentParser(description="Process old buildings grid data.")
    parser.add_argument('--simulate', action='store_true', help="Force simulated 250m subdivision from 1km data")
    parser.add_argument('--threshold', type=float, default=250.0, help="Total buildings threshold for 250m grid (default: 250.0)")
    args = parser.parse_args()

    data_dir = 'data'
    output_dir = 'public/data'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'old_buildings_ratio.geojson')
    
    # 1. Detect 250M zip files
    old_250m_files = glob.glob(os.path.join(data_dir, '*(B100)국토통계_건축물-시기별 건축물 수(35년 이상)-(격자) 250M_*.zip'))
    total_250m_files = glob.glob(os.path.join(data_dir, '*(B100)국토통계_건축물-건축물 수 합계 통계-(격자) 250M_*.zip'))
    
    has_250m_files = len(old_250m_files) > 0 and len(total_250m_files) > 0
    
    resolution = '1km'
    
    if has_250m_files and not args.simulate:
        print("Detected 250M grid files. Running in official 250m grid mode.")
        resolution = '250m'
        old_patterns = ['*(B100)국토통계_건축물-시기별 건축물 수(35년 이상)-(격자) 250M_*.zip']
        total_patterns = ['*(B100)국토통계_건축물-건축물 수 합계 통계-(격자) 250M_*.zip']
    else:
        if args.simulate:
            print("Force simulation option enabled. Loading 1KM grid files for 250m simulation...")
            resolution = '250m_sim'
        else:
            print("250M grid files not found. Running in fallback 1KM grid mode.")
            resolution = '1km'
            
        old_patterns = ['*(B100)국토통계_건축물-시기별 건축물 수(35년 이상)-(격자) 1KM_*.zip']
        total_patterns = [
            '*(B100)국토통계_건축물-건축물 수 합계 통계-(격자) 1KM_*.zip',
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
    total_df = total_gdf.drop(columns=['geometry']).rename(columns={'val': 'total_val'})
    merged_gdf = old_gdf.merge(total_df, on='gid', how='inner')
    merged_gdf['ratio'] = merged_gdf['val'] / merged_gdf['total_val']
    
    # Apply filtering/subdivision based on mode
    if resolution == '250m':
        # Official 250M grid filter: ratio >= 60% and total_val >= 250
        filtered_gdf = merged_gdf[(merged_gdf['ratio'] >= 0.6) & (merged_gdf['total_val'] >= 250)].copy()
        filtered_gdf['resolution'] = '250m'
        
    elif resolution == '250m_sim':
        # Simulated 250m subdivision.
        filtered_gdf = subdivide_to_250m(merged_gdf, threshold_val_250m=args.threshold)
        filtered_gdf['resolution'] = '250m'
        
    else:
        # Fallback 1KM grid filter: (ratio >= 60% and total_val >= 500) or old_val >= 1000
        filtered_gdf = merged_gdf[((merged_gdf['total_val'] >= 500) & (merged_gdf['ratio'] >= 0.6)) | (merged_gdf['val'] >= 1000)].copy()
        filtered_gdf['resolution'] = '1km'
        
    print(f"Found {len(filtered_gdf)} grids matching criteria.")
    
    if filtered_gdf.empty:
        print("No grids found matching the criteria.")
        return
        
    print("Reprojecting to EPSG:4326...")
    filtered_gdf = filtered_gdf.to_crs(epsg=4326)
    
    # Keep necessary columns
    filtered_gdf['ratio_pct'] = (filtered_gdf['ratio'] * 100).round(1)
    # Convert numeric fields to clean types
    filtered_gdf['val'] = filtered_gdf['val'].round(1)
    filtered_gdf['total_val'] = filtered_gdf['total_val'].round(1)
    
    final_gdf = filtered_gdf[['gid', 'val', 'total_val', 'ratio_pct', 'resolution', 'geometry']]
    
    print("Saving to GeoJSON...")
    final_gdf.to_file(output_file, driver='GeoJSON')
    print(f"Successfully saved to {output_file} (Resolution: {resolution})")

if __name__ == '__main__':
    process_data()
