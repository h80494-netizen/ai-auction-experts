import geopandas as gpd
import sqlite3
import json
import os

DB_PATH = 'backend/data/map_data.db'
GPKG_PATH = 'data/경기강원계획관리.gpkg'

def import_gpkg():
    print(f"Loading {GPKG_PATH}...")
    gdf = gpd.read_file(GPKG_PATH)
    
    if gdf.crs is None or gdf.crs.to_string() != 'EPSG:4326':
        print(f"Reprojecting from {gdf.crs} to EPSG:4326...")
        gdf = gdf.to_crs(epsg=4326)
    
    print("Connecting to SQLite...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Optional: Delete existing '계획관리지역' to avoid duplicates on re-run
    cursor.execute("DELETE FROM zoning_polygons WHERE name='계획관리지역'")
    
    print(f"Inserting {len(gdf)} features...")
    count = 0
    for idx, row in gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
            
        bounds = geom.bounds # (minx, miny, maxx, maxy) -> (min_lng, min_lat, max_lng, max_lat)
        min_lng, min_lat, max_lng, max_lat = bounds
        
        geojson_str = json.dumps(geom.__geo_interface__)
        
        cursor.execute('''
            INSERT INTO zoning_polygons (name, propel_cd, geojson, min_lat, max_lat, min_lng, max_lng)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('계획관리지역', '계획관리지역', geojson_str, min_lat, max_lat, min_lng, max_lng))
        
        count += 1
        
    conn.commit()
    conn.close()
    print(f"Successfully inserted {count} polygons.")

if __name__ == '__main__':
    import_gpkg()
