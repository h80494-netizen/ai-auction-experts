import sqlite3
import geopandas as gpd
import json
import os
import sys

def process_layer(zip_uri, table_name, db_path):
    try:
        print(f"\n--- Processing {table_name} from {zip_uri} ---")
        gdf = gpd.read_file(zip_uri, encoding='cp949')
        
        print(f"Original CRS: {gdf.crs}")
        if gdf.crs is None:
            print("CRS is missing, assuming EPSG:5174.")
            gdf.set_crs(epsg=5174, inplace=True)
            
        print("Converting CRS to EPSG:4326...")
        gdf = gdf.to_crs(epsg=4326)
        
        print("Simplifying geometries for performance...")
        # 0.00005 degrees is roughly 5 meters, which provides excellent detail while keeping payloads lightweight
        gdf['geometry'] = gdf['geometry'].simplify(0.00005, preserve_topology=True)
        
        print(f"Connecting to database {db_path}...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        cursor.execute(f'''
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                propel_cd TEXT,
                min_lat REAL,
                max_lat REAL,
                min_lng REAL,
                max_lng REAL,
                geojson TEXT
            )
        ''')
        
        count = 0
        for idx, row in gdf.iterrows():
            geom = row['geometry']
            if geom is None or geom.is_empty:
                continue
                
            bounds = geom.bounds # (minx, miny, maxx, maxy) -> (min_lng, min_lat, max_lng, max_lat)
            min_lng, min_lat, max_lng, max_lat = bounds
            
            geojson_str = json.dumps(geom.__geo_interface__)
            
            # Use 'DGM_NM' as the name, fall back to index if not present
            name = str(row['DGM_NM']) if 'DGM_NM' in row else f"{table_name} {idx}"
            propel_cd = str(row['PROPEL_CD']) if 'PROPEL_CD' in row and row['PROPEL_CD'] is not None else None
            
            cursor.execute(f'''
                INSERT INTO {table_name} (name, propel_cd, min_lat, max_lat, min_lng, max_lng, geojson)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, propel_cd, min_lat, max_lat, min_lng, max_lng, geojson_str))
            
            count += 1
            
        conn.commit()
        
        # Create spatial query indexes
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_min_lat ON {table_name}(min_lat)")
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_max_lat ON {table_name}(max_lat)")
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_min_lng ON {table_name}(min_lng)")
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_max_lng ON {table_name}(max_lng)")
        
        conn.close()
        print(f"Successfully processed and inserted {count} polygons into '{table_name}' table.")
        
    except Exception as e:
        print(f"Error in {table_name} processing: {e}")

def main():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'map_data.db')
    
    # 1. Process Redevelopment/Reconstruction (서울지역 재개발재건축)
    zip_uq120 = "zip://data/UQ120_도시계획사업(서울플랜+)_202602 (1).zip!945_UQ120_도시계획사업(서울플랜+)_202602/shp파일"
    process_layer(zip_uq120, "redevelopment_zones", db_path)
    
    # 2. Process Zoning (용도지역)
    zip_uq111 = "zip://data/UQ111_용도지역(도시지역)_202602.zip!shp파일"
    process_layer(zip_uq111, "zoning_polygons", db_path)

if __name__ == '__main__':
    main()
