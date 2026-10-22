import os
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
import warnings
warnings.filterwarnings('ignore')

def main():
    input_file = 'public/data/old_buildings_ratio.geojson'
    
    print(f"Loading {input_file}...")
    gdf = gpd.read_file(input_file)
    
    print("Downloading water bodies for Seoul via osmnx...")
    try:
        water_gdf = ox.features_from_place('Seoul, South Korea', tags={'natural': 'water'})
    except Exception as e:
        print("Failed to download water bodies:", e)
        return
        
    if water_gdf.empty:
        print("No water found.")
        return
        
    print("Dissolving water geometries into a single multipolygon...")
    # Filter for Han River (name contains 한강)
    han_river = water_gdf[water_gdf['name'].str.contains('한강', na=False)]
    
    if han_river.empty:
        # If no explicit name, just take all large water bodies
        han_river = water_gdf
        
    water_union = han_river.geometry.buffer(0).unary_union
    
    print("Calculating difference (Grid - Water)...")
    gdf['geometry'] = gdf.geometry.buffer(0)
    gdf['geometry'] = gdf.geometry.difference(water_union)
    
    def keep_polygons(geom):
        if geom.geom_type in ['Polygon', 'MultiPolygon']:
            return geom
        elif geom.geom_type == 'GeometryCollection':
            polys = [g for g in geom.geoms if g.geom_type in ['Polygon', 'MultiPolygon']]
            if not polys:
                return Polygon()
            return MultiPolygon(polys) if len(polys) > 1 else polys[0]
        return Polygon()
        
    gdf['geometry'] = gdf.geometry.apply(keep_polygons)
    gdf = gdf[~gdf.geometry.is_empty]
    
    print("Saving clipped data...")
    if os.path.exists(input_file):
        os.remove(input_file)
    gdf.to_file(input_file, driver='GeoJSON')
    print("Successfully clipped Han River from grids!")

if __name__ == '__main__':
    main()
