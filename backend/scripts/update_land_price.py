import pandas as pd
import geopandas as gpd
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/map_data.db')
SHP_PATHS = {
    '서울': os.path.join(os.path.dirname(__file__), '../../data/서울공시지가.shp'),
    '경기': os.path.join(os.path.dirname(__file__), '../../data/경기공시지가.shp'),
    '인천': os.path.join(os.path.dirname(__file__), '../../data/인천공시지가.shp')
}

def get_region(addr):
    if not addr: return '기타'
    if addr.startswith('서울'): return '서울'
    if addr.startswith('경기'): return '경기'
    if addr.startswith('인천'): return '인천'
    return '기타'

def main():
    print("Connecting to DB...")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('SELECT id, case_no, address, lat, lng FROM auctions WHERE lat > 0 AND lng > 0', conn)
    print(f"Loaded {len(df)} properties with coordinates.")

    df['region'] = df['address'].apply(get_region)

    # Convert to GeoDataFrame (EPSG:4326)
    gdf_auctions = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.lng, df.lat), crs="EPSG:4326"
    )
    # Convert to EPSG:5186 to match shapefiles
    gdf_auctions = gdf_auctions.to_crs(epsg=5186)

    updates = []

    for region, shp_path in SHP_PATHS.items():
        region_auctions = gdf_auctions[gdf_auctions['region'] == region]
        if len(region_auctions) == 0:
            print(f"No properties found for {region}")
            continue

        print(f"\nProcessing {region} ({len(region_auctions)} properties)...")
        if not os.path.exists(shp_path):
            print(f"Shapefile not found: {shp_path}")
            continue

        try:
            print(f"Reading shapefile for {region}...")
            # We only need geometry and A10 (official land price)
            # Some shapefiles might have different column names, so we'll read all columns
            shp = gpd.read_file(shp_path)
            print(f"Loaded {len(shp)} points from shapefile.")

            # Identify the price column
            price_col = 'A10'
            if 'A10' not in shp.columns:
                print(f"Warning: A10 not in {region} shapefile columns: {shp.columns}")
                # Fallback to look for JIGA or similar
                for c in shp.columns:
                    if 'JIGA' in c.upper() or 'PRICE' in c.upper():
                        price_col = c
                        break

            if price_col not in shp.columns:
                print(f"Failed to find price column for {region}. Skipping.")
                continue

            print(f"Using column {price_col} for land price.")

            # Drop missing geometries to avoid sjoin errors
            shp = shp.dropna(subset=['geometry'])

            # Spatial join (nearest)
            print(f"Performing spatial join (nearest) for {region}...")
            # We want to keep all region_auctions and just attach the nearest shapefile attributes
            joined = gpd.sjoin_nearest(region_auctions, shp[['geometry', price_col]], how='left', distance_col='dist')
            
            # The join might produce duplicates if multiple nearest neighbors are found at exact same distance.
            # Drop duplicates by 'id'
            joined = joined.drop_duplicates(subset=['id'])

            for idx, row in joined.iterrows():
                try:
                    price = float(row[price_col]) if not pd.isna(row[price_col]) else 0.0
                except:
                    price = 0.0
                updates.append((price, int(row['id'])))
            
            print(f"Prepared {len(joined)} updates for {region}.")

        except Exception as e:
            print(f"Error processing {region}: {e}")

    if updates:
        print(f"\nExecuting {len(updates)} database updates...")
        cursor = conn.cursor()
        cursor.executemany('UPDATE auctions SET official_land_price = ? WHERE id = ?', updates)
        conn.commit()
        print("Database update complete!")
    else:
        print("No updates prepared.")

    conn.close()

if __name__ == '__main__':
    main()
