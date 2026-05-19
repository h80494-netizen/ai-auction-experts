import os
import sqlite3
import geopandas as gpd

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/map_data.db')
SHP_PATH = os.path.join(os.path.dirname(__file__), '../../data/산업단지/DAM_YUCH.shp')

def import_inds():
    print(f"Loading shapefile from {SHP_PATH}...")
    gdf = gpd.read_file(SHP_PATH, encoding='euc-kr')
    
    print("Dissolving by DAN_ID...")
    gdf_dissolved = gdf.dissolve(by='DAN_ID').reset_index()
    
    print("Converting to EPSG:4326 and calculating centroids...")
    # EPSG:5186 to EPSG:4326 for web map compatibility
    gdf_4326 = gdf_dissolved.to_crs(epsg=4326)
    gdf_centroids = gdf_4326.copy()
    gdf_centroids['geometry'] = gdf_4326.geometry.centroid
    
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Recreate the table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS industrial_complexes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        lat REAL,
        lng REAL
    )
    ''')
    cursor.execute('DELETE FROM industrial_complexes')
    
    count = 0
    for idx, row in gdf_centroids.iterrows():
        # name can be derived from UPJ6 if needed, but it's not a clear name
        # We'll just call it '산업단지' or extract the first word from UPJ6 if it looks like a name
        name = "산업단지"
        lat = row.geometry.y
        lng = row.geometry.x
        
        cursor.execute("INSERT INTO industrial_complexes (name, lat, lng) VALUES (?, ?, ?)", (name, lat, lng))
        count += 1
        
    conn.commit()
    conn.close()
    print(f"Successfully inserted {count} industrial complex centroids into the database.")

if __name__ == '__main__':
    import_inds()
