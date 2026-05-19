import os
import zipfile
import tempfile
import glob
import geopandas as gpd
import pandas as pd

def process_data():
    data_dir = 'data'
    output_dir = 'public/data'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'old_buildings.geojson')
    
    # 35년 이상 건축물 수 zip 파일 찾기
    zip_files = glob.glob(os.path.join(data_dir, '*(B100)국토통계_건축물-시기별 건축물 수(35년 이상)-(격자)*.zip'))
    
    if not zip_files:
        print("Zip files not found.")
        return

    gdfs = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for zip_path in zip_files:
            print(f"Processing {zip_path}...")
            # Extract zip
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Some zip files have encoding issues with korean filenames, but we can extract all
                zip_ref.extractall(temp_dir)
            
            # Find the .shp file in temp_dir
            shp_files = glob.glob(os.path.join(temp_dir, '*.shp'))
            if not shp_files:
                print(f"No .shp found in {zip_path}")
                continue
                
            shp_file = shp_files[0]
            
            # Read shapefile
            # encoding='cp949' or 'euc-kr' might be needed for korean attributes
            gdf = gpd.read_file(shp_file, encoding='cp949')
            
            # Reproject from EPSG:5179 to EPSG:4326
            if gdf.crs is None:
                gdf.set_crs(epsg=5179, inplace=True)
            gdf = gdf.to_crs(epsg=4326)
            
            # Keep only necessary columns to reduce file size
            # Usually 'val' holds the count
            if 'val' in gdf.columns:
                gdf = gdf[['val', 'geometry']]
                # Drop rows where val is 0 or NaN to save space
                gdf = gdf[gdf['val'] > 0]
                gdfs.append(gdf)
            else:
                print(f"'val' column not found in {shp_file}")
            
            # Clean up extracted files for next iteration
            for f in glob.glob(os.path.join(temp_dir, '*')):
                os.remove(f)

    if gdfs:
        print("Concatenating all regions...")
        final_gdf = pd.concat(gdfs, ignore_index=True)
        # Convert val to integer if possible
        final_gdf['val'] = final_gdf['val'].fillna(0).astype(int)
        
        print("Saving to GeoJSON...")
        final_gdf.to_file(output_file, driver='GeoJSON')
        print(f"Successfully saved to {output_file}")
    else:
        print("No data processed.")

if __name__ == '__main__':
    process_data()
