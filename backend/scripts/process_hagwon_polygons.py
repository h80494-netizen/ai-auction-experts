import pandas as pd
import sqlite3
import os
import numpy as np
from sklearn.cluster import DBSCAN
from scipy.spatial import ConvexHull
import json

CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/서울학원.xlsx')
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/map_data.db')

def process_hagwons():
    print("Loading Seoul Hagwon Excel...")
    try:
        df = pd.read_excel(CSV_PATH)
    except Exception as e:
        print(f"Failed to load Excel: {e}")
        return

    print(f"Total rows loaded: {len(df)}")
    
    # Find '경도' and '위도' in columns
    lat_col_name = None
    lng_col_name = None
    for col in df.columns:
        if '경도' in str(col):
            lng_col_name = col
        if '위도' in str(col):
            lat_col_name = col
            
    if not lat_col_name or not lng_col_name:
        lng_col_name = df.columns[-2]
        lat_col_name = df.columns[-1]

    print(f"Extracted coordinate columns: Lng={lng_col_name}, Lat={lat_col_name}")

    lat_col = lat_col_name
    lng_col = lng_col_name

    # Filter out missing coordinates
    df = df.dropna(subset=[lat_col, lng_col])
    # Convert to numeric just in case
    df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
    df[lng_col] = pd.to_numeric(df[lng_col], errors='coerce')
    df = df.dropna(subset=[lat_col, lng_col])
    
    # Filter reasonable coordinates for Korea (lat: 33~39, lng: 124~130)
    df = df[(df[lat_col] > 33) & (df[lat_col] < 39) & (df[lng_col] > 124) & (df[lng_col] < 130)]
    
    print(f"Valid coordinates: {len(df)}")

    if len(df) == 0:
        print("No valid data to process.")
        return

    print("Running DBSCAN clustering (radius: 200m, min_samples: 30)...")
    # Haversine distance requires radians
    coords = np.radians(df[[lat_col, lng_col]].values)
    
    kms_per_radian = 6371.0088
    epsilon = 0.2 / kms_per_radian # 200 meters
    
    db = DBSCAN(eps=epsilon, min_samples=30, algorithm='ball_tree', metric='haversine').fit(coords)
    df['cluster'] = db.labels_
    
    # -1 means noise (not in any cluster)
    clusters = df[df['cluster'] != -1]
    num_clusters = clusters['cluster'].nunique()
    print(f"Found {num_clusters} hagwon clusters.")

    polygons = []
    
    for cluster_id, group in clusters.groupby('cluster'):
        points = group[[lat_col, lng_col]].values
        
        # We need at least 3 points to make a polygon
        if len(points) >= 3:
            try:
                hull = ConvexHull(points)
                # hull.vertices contains the indices of points forming the convex hull in counterclockwise order
                hull_points = points[hull.vertices]
                
                # Leaflet expects [lat, lng] array of arrays for polygons
                # Convert to Python lists
                poly_coords = hull_points.tolist()
                
                # Close the polygon if necessary (though Leaflet usually handles unclosed polygons fine, it's good practice)
                # poly_coords.append(poly_coords[0]) 
                
                polygons.append({
                    "cluster_id": int(cluster_id),
                    "count": len(group),
                    "coordinates": poly_coords
                })
            except Exception as e:
                print(f"Could not compute Convex Hull for cluster {cluster_id}: {e}")

    print(f"Generated {len(polygons)} polygons.")

    print("Saving to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hagwon_polygons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            count INTEGER,
            coordinates_json TEXT
        )
    ''')
    cursor.execute('DELETE FROM hagwon_polygons')
    
    for poly in polygons:
        cursor.execute(
            'INSERT INTO hagwon_polygons (count, coordinates_json) VALUES (?, ?)',
            (poly['count'], json.dumps(poly['coordinates']))
        )
        
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == '__main__':
    process_hagwons()
