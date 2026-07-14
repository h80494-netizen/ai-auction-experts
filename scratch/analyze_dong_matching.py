# -*- coding: utf-8 -*-
import geopandas as gpd
import sqlite3
import json
from shapely.geometry import Point, shape
import os

db_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"
shp_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\gris_shp\Gyeonggi_Jeongbi_Guyeok.shp"

def main():
    if not os.path.exists(db_path):
        print("DB not found!")
        return
    if not os.path.exists(shp_path):
        print("Shapefile not found!")
        return

    # 1. Load Shapefile
    print("Loading Shapefile...")
    gdf = gpd.read_file(shp_path, encoding='cp949')
    print(f"Loaded {len(gdf)} Shapefile polygons.")

    # Add index for easy reference
    gdf['shp_idx'] = gdf.index

    # 2. Load Gyeonggi OpenAPI rows from DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, propel_cd, min_lat, max_lat, min_lng, max_lng FROM redevelopment_zones WHERE name LIKE '[경기]%'")
    db_rows = cursor.fetchall()
    conn.close()
    print(f"Loaded {len(db_rows)} Gyeonggi zones from database.")

    # 3. Parse DB rows into a list of dicts
    parsed_db = []
    for r in db_rows:
        rid, dname, propel_cd, min_lat, max_lat, min_lng, max_lng = r
        zone_name = ""
        biz_type = ""
        stage = ""
        try:
            if dname.startswith("[경기]"):
                parts = dname[4:].split("(")
                zone_name = parts[0].strip()
                if len(parts) > 1:
                    sub_parts = parts[1].replace(")", "").split(",")
                    biz_type = sub_parts[0].strip()
                    if len(sub_parts) > 1:
                        stage = sub_parts[1].strip()
        except Exception:
            pass
        
        c_lat = (min_lat + max_lat) / 2.0
        c_lng = (min_lng + max_lng) / 2.0
        
        parsed_db.append({
            "db_id": rid,
            "display_name": dname,
            "zone_name": zone_name,
            "propel_cd": propel_cd,
            "biz_type": biz_type,
            "stage": stage,
            "lat": c_lat,
            "lng": c_lng,
            "geometry": Point(c_lng, c_lat)
        })

    # 4. Create GeoDataFrame for DB points
    db_gdf = gpd.GeoDataFrame(parsed_db, geometry="geometry")
    db_gdf.set_crs(epsg=4326, inplace=True)

    # 5. Spatial Join (DB Points within Shapefile Polygons)
    print("Performing spatial join...")
    joined = gpd.sjoin(db_gdf, gdf, how="left", predicate="within")
    
    # 6. Analyze Matches
    spatial_matched_count = 0
    name_matched_count = 0
    both_matched_count = 0
    no_matched_count = 0
    
    final_matches = {} # db_id -> shp_idx

    for idx, row in joined.iterrows():
        db_id = row['db_id']
        shp_idx = row['shp_idx'] # can be NaN if no spatial match
        zone_name = row['zone_name']
        
        has_spatial = not gpd.pd.isna(shp_idx)
        has_name = False
        name_candidate_idx = None
        
        # Check text match
        if zone_name:
            for shp_i, shp_row in gdf.iterrows():
                s_name = str(shp_row['name']) if shp_row['name'] else ""
                s_remark = str(shp_row['remark']) if shp_row['remark'] else ""
                if zone_name in s_name or s_name and s_name in zone_name or zone_name in s_remark:
                    has_name = True
                    name_candidate_idx = shp_i
                    break

        if has_spatial and has_name and int(shp_idx) == name_candidate_idx:
            both_matched_count += 1
            final_matches[db_id] = int(shp_idx)
        elif has_spatial:
            spatial_matched_count += 1
            final_matches[db_id] = int(shp_idx)
        elif has_name:
            name_matched_count += 1
            final_matches[db_id] = name_candidate_idx
        else:
            no_matched_count += 1

    print(f"\nMatching Summary:")
    print(f"  Both spatial and name matched: {both_matched_count}")
    print(f"  Spatial matched only: {spatial_matched_count}")
    print(f"  Name matched only: {name_matched_count}")
    print(f"  No match: {no_matched_count}")
    print(f"  Total DB rows processed: {len(parsed_db)}")
    print(f"  Unique Shapefile Polygons matched: {len(set(final_matches.values()))} / {len(gdf)}")

if __name__ == '__main__':
    main()
