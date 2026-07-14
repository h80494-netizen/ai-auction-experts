import sqlite3
import geopandas as gpd
import json
import sys

def main():
    try:
        print("Reading shapefile from zip...")
        # geopandas can read shapefiles directly from a zip
        gdf = gpd.read_file('zip://data/개발행위허가제한지역.zip')
        
        print(f"Original CRS: {gdf.crs}")
        if gdf.crs is None:
            print("CRS is missing, assuming EPSG:5174 based on prj file.")
            gdf.set_crs(epsg=5174, inplace=True)
            
        print("Converting CRS to EPSG:4326...")
        gdf = gdf.to_crs(epsg=4326)
        
        print("Simplifying geometries for performance...")
        # Convert to a slightly simplified geometry to reduce JSON payload size
        # 0.0001 degrees is roughly 10 meters, good enough for map rendering
        gdf['geometry'] = gdf['geometry'].simplify(0.0001, preserve_topology=True)
        
        print("Connecting to database...")
        conn = sqlite3.connect('backend/data/map_data.db')
        cursor = conn.cursor()
        
        cursor.execute("DROP TABLE IF EXISTS district_units")
        cursor.execute('''
            CREATE TABLE district_units (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                min_lat REAL,
                max_lat REAL,
                min_lng REAL,
                max_lng REAL,
                geojson TEXT
            )
        ''')
        
        # Determine the name column, usually one of 'DGM_NM', 'NAME', '구역명'
        name_col = None
        for col in gdf.columns:
            if 'NM' in col.upper() or 'NAME' in col.upper() or '명' in col:
                name_col = col
                break
                
        count = 0
        for idx, row in gdf.iterrows():
            geom = row['geometry']
            if geom is None or geom.is_empty:
                continue
                
            bounds = geom.bounds # (minx, miny, maxx, maxy) -> (min_lng, min_lat, max_lng, max_lat)
            min_lng, min_lat, max_lng, max_lat = bounds
            
            geojson_str = json.dumps(geom.__geo_interface__)
            name = str(row[name_col]) if name_col else f"개발행위허가제한지역 {idx}"
            
            cursor.execute('''
                INSERT INTO district_units (name, min_lat, max_lat, min_lng, max_lng, geojson)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, min_lat, max_lat, min_lng, max_lng, geojson_str))
            
            count += 1
            
        conn.commit()
        
        # Create indexes for fast spatial querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_du_min_lat ON district_units(min_lat)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_du_max_lat ON district_units(max_lat)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_du_min_lng ON district_units(min_lng)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_du_max_lng ON district_units(max_lng)")
        
        conn.close()
        print(f"Successfully processed and inserted {count} district unit polygons into database.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
