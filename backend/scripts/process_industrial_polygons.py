import os
import sqlite3
import geopandas as gpd
import zipfile
import tempfile
import json
import shapely

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/map_data.db')
ZIP_PATH = os.path.join(os.path.dirname(__file__), '../../data/산업단지/전국산업단지.zip')

def process_inds():
    # We create a temporary directory to extract the shapefile
    print(f"Extracting {ZIP_PATH}...")
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)
        
        # Find the .shp file
        shp_file = None
        for file in os.listdir(tmpdir):
            if file.endswith('.shp'):
                shp_file = os.path.join(tmpdir, file)
                break
                
        if not shp_file:
            print("No .shp file found in the zip archive.")
            return

        print(f"Loading shapefile: {shp_file}")
        # The file is AL_D060_00_20260719.shp
        # Korea standard node/link usually uses CP949 or EUC-KR encoding for attributes
        try:
            gdf = gpd.read_file(shp_file, encoding='cp949')
        except:
            gdf = gpd.read_file(shp_file, encoding='utf-8')
            
    print("Projecting to EPSG:5179 to calculate 1km buffer in meters...")
    # Nationwide standard for this AL_D060 usually is EPSG:5179 (Korea 2000 Central Belt)
    # Let's set CRS if none. If none, assume 5179.
    if gdf.crs is None:
        gdf.set_crs(epsg=5179, inplace=True)
    else:
        gdf = gdf.to_crs(epsg=5179)
        
    print("Calculating buffers (1000m)...")
    # Buffer by 1000 meters
    gdf_buffered = gdf.copy()
    gdf_buffered['geometry'] = gdf.geometry.buffer(1000)
    
    print("Converting original and buffered geometries to EPSG:4326 for Web Map...")
    gdf_4326 = gdf.to_crs(epsg=4326)
    gdf_buffered_4326 = gdf_buffered.to_crs(epsg=4326)
    
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS industrial_polygons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        polygon_geojson TEXT,
        buffer_geojson TEXT,
        min_lat REAL,
        max_lat REAL,
        min_lng REAL,
        max_lng REAL
    )
    ''')
    cursor.execute('DELETE FROM industrial_polygons')
    
    print("Inserting data into DB...")
    count = 0
    for idx in range(len(gdf_4326)):
        geom = gdf_4326.iloc[idx].geometry
        buffered_geom = gdf_buffered_4326.iloc[idx].geometry
        
        if geom is None or geom.is_empty:
            continue
            
        bounds = geom.bounds # minx, miny, maxx, maxy (lng, lat, lng, lat)
        
        # Depending on attribute name, we might have A1, A2, etc. Let's just use '산업단지' if name is missing.
        # Check if any common name column exists
        name = '산업단지'
        name_cols = ['NAM', 'NAME', 'A3', '단지명']
        for col in name_cols:
            if col in gdf_4326.columns:
                name = str(gdf_4326.iloc[idx][col])
                break
                
        geom_json = shapely.to_geojson(geom)
        buffered_json = shapely.to_geojson(buffered_geom)
        
        cursor.execute('''
            INSERT INTO industrial_polygons 
            (name, polygon_geojson, buffer_geojson, min_lat, max_lat, min_lng, max_lng)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, 
            geom_json, 
            buffered_json, 
            bounds[1], bounds[3], bounds[0], bounds[2]
        ))
        count += 1
        
        if count % 500 == 0:
            print(f"Inserted {count} records...")
            
    conn.commit()
    
    # Also create index
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ind_poly_bounds ON industrial_polygons(min_lat, max_lat, min_lng, max_lng)')
    
    conn.close()
    print(f"Successfully processed and inserted {count} industrial polygons with 1km buffers.")

if __name__ == '__main__':
    process_inds()
