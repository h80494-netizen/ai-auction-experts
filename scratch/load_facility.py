import geopandas as gpd
import sqlite3
import pandas as pd
from shapely.geometry import Point

print('Loading DAM_YOJ.shp from data/시설용지도면.zip')
try:
    gdf = gpd.read_file('zip://data/시설용지도면.zip!DAM_YOJ.shp', encoding='euc-kr')
    print('Initial CRS:', gdf.crs)
    gdf = gdf.to_crs('EPSG:4326')

    centroids = gdf.geometry.centroid
    gdf['lng'] = centroids.x
    gdf['lat'] = centroids.y

    conn = sqlite3.connect('backend/data/map_data.db')
    c = conn.cursor()

    c.execute('DELETE FROM industrial_complexes')
    inserted = 0
    for idx, row in gdf.iterrows():
        yoj_id = row.get("YOJ_ID", "")
        name = f'시설용지 ({yoj_id})' if yoj_id else '시설용지'
        c.execute('INSERT INTO industrial_complexes (name, lat, lng) VALUES (?, ?, ?)',
                  (name, row['lat'], row['lng']))
        inserted += 1

    conn.commit()
    conn.close()
    print(f'Successfully inserted {inserted} facilities into industrial_complexes table.')
except Exception as e:
    print(f'Error: {e}')
