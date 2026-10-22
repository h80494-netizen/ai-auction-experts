import os
import sqlite3
import geopandas as gpd
import pandas as pd
import zipfile
import tempfile
import shutil
import json
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

DB_PATH = 'backend/data/map_data.db'
ZIP_PATH = 'data/전국장기미집행.zip'

def get_year_from_ntfc_sn(ntfc_sn):
    if pd.isna(ntfc_sn) or not isinstance(ntfc_sn, str):
        return None
    # NTFC_SN format: e.g. 11110NTC202008270010 (length usually 22)
    # The 'NTC' is followed by YYYYMMDD
    idx = ntfc_sn.find('NTC')
    if idx != -1 and len(ntfc_sn) >= idx + 7:
        year_str = ntfc_sn[idx+3:idx+7]
        if year_str.isdigit():
            return int(year_str)
    return None

def process_shapefile(gdf, cursor):
    # Filter 1: EXCUT_SE == 'EMA0001' (미집행)
    if 'EXCUT_SE' not in gdf.columns:
        return 0
    gdf = gdf[gdf['EXCUT_SE'] == 'EMA0001']
    if gdf.empty:
        return 0
        
    current_year = datetime.now().year
    count = 0
    
    # Process each row
    for idx, row in gdf.iterrows():
        geom = row['geometry']
        if geom is None or geom.is_empty:
            continue
            
        # Filter 2: 10 years or older (10년 이상)
        gosi_year = get_year_from_ntfc_sn(row.get('NTFC_SN'))
        if gosi_year is None:
            # Fallback to CREATE_DAT
            create_dat = str(row.get('CREATE_DAT', ''))
            if len(create_dat) >= 4 and create_dat[:4].isdigit():
                gosi_year = int(create_dat[:4])
        
        if gosi_year is None or (current_year - gosi_year) < 10:
            continue
            
        # Ensure CRS is EPSG:4326 before getting bounds and dumping geojson
        # Convert single geometry to GeoSeries to use to_crs
        gs = gpd.GeoSeries([geom], crs=gdf.crs)
        gs_4326 = gs.to_crs(epsg=4326)
        geom_4326 = gs_4326.iloc[0]
        
        # Simplify geometry to save space
        geom_4326 = geom_4326.simplify(0.0001, preserve_topology=True)
        
        bounds = geom_4326.bounds
        if bounds is None or len(bounds) != 4:
            continue
        min_lng, min_lat, max_lng, max_lat = bounds
        
        name = str(row.get('DGM_NM', '이름없음'))
        geojson_str = json.dumps(geom_4326.__geo_interface__)
        
        cursor.execute('''
            INSERT INTO unexecuted_facilities (name, min_lat, max_lat, min_lng, max_lng, geojson, gosi_year)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, min_lat, max_lat, min_lng, max_lng, geojson_str, gosi_year))
        
        count += 1
        
    return count

def main():
    if not os.path.exists(ZIP_PATH):
        print(f"Zip file not found: {ZIP_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS unexecuted_facilities")
    cursor.execute('''
        CREATE TABLE unexecuted_facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            min_lat REAL,
            max_lat REAL,
            min_lng REAL,
            max_lng REAL,
            geojson TEXT,
            gosi_year INTEGER
        )
    ''')
    
    temp_dir = tempfile.mkdtemp()
    total_inserted = 0
    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as z:
            target_files = [f for f in z.namelist() if f.endswith('.zip') and ('11000' in f or '28000' in f or '41000' in f)]
            for zip_name in target_files:
                print(f"Processing {zip_name}...")
                z.extract(zip_name, temp_dir)
                inner_zip_path = os.path.join(temp_dir, zip_name)
                
                inner_dir = os.path.join(temp_dir, 'inner')
                if os.path.exists(inner_dir):
                    shutil.rmtree(inner_dir)
                os.makedirs(inner_dir, exist_ok=True)
                
                with zipfile.ZipFile(inner_zip_path, 'r') as z2:
                    z2.extractall(inner_dir)
                
                # Find all .shp files
                shp_files = [f for f in os.listdir(inner_dir) if f.endswith('.shp')]
                for shp_name in shp_files:
                    shp_path = os.path.join(inner_dir, shp_name)
                    try:
                        gdf = gpd.read_file(shp_path, encoding='euc-kr')
                    except Exception:
                        gdf = gpd.read_file(shp_path, encoding='utf-8')
                        
                    if gdf.crs is None:
                        gdf.set_crs(epsg=5174, inplace=True) # Assume 5174 for Korean public data
                        
                    inserted = process_shapefile(gdf, cursor)
                    total_inserted += inserted
                    print(f"  Inserted {inserted} records from {shp_name}")
                    
        conn.commit()
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_uf_min_lat ON unexecuted_facilities(min_lat)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_uf_max_lat ON unexecuted_facilities(max_lat)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_uf_min_lng ON unexecuted_facilities(min_lng)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_uf_max_lng ON unexecuted_facilities(max_lng)")
        conn.commit()
        
        print(f"Data processing completed successfully! Total records: {total_inserted}")
        
    finally:
        shutil.rmtree(temp_dir)
        conn.close()

if __name__ == '__main__':
    main()
