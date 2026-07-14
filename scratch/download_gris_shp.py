# -*- coding: utf-8 -*-
import requests
import json
import os
import zipfile
import geopandas as gpd
from shapely.geometry import shape

def esri_to_geojson(esri_feature):
    esri_geom = esri_feature.get("geometry", {})
    properties = esri_feature.get("attributes", {})
    
    # Clean up property keys to avoid encoding issue or null values
    cleaned_properties = {}
    for k, v in properties.items():
        # Shapefile field names must be <= 10 characters
        # Let's map standard fields to short names
        if k == "OBJECTID": cleaned_properties["id"] = v
        elif k == "MNUM": cleaned_properties["mnum"] = str(v) if v else ""
        elif k == "ALIAS": cleaned_properties["name"] = str(v) if v else ""
        elif k == "REMARK": cleaned_properties["remark"] = str(v) if v else ""
        elif k == "NTFDATE": cleaned_properties["ntfdate"] = str(v) if v else ""
        elif k == "COL_ADM_SECT_CD": cleaned_properties["sgg_cd"] = str(v) if v else ""
        else:
            cleaned_properties[k[:10].lower()] = str(v) if v else ""

    geojson_geom = None
    if "rings" in esri_geom:
        geojson_geom = {
            "type": "Polygon",
            "coordinates": esri_geom["rings"]
        }
    elif "paths" in esri_geom:
        geojson_geom = {
            "type": "LineString",
            "coordinates": esri_geom["paths"][0]
        }
    elif "x" in esri_geom and "y" in esri_geom:
        geojson_geom = {
            "type": "Point",
            "coordinates": [esri_geom["x"], esri_geom["y"]]
        }
        
    if not geojson_geom:
        return None
        
    return {
        "type": "Feature",
        "geometry": geojson_geom,
        "properties": cleaned_properties
    }

def fetch_and_save_shp(lid, name, out_dir):
    url = f"https://gris.gg.go.kr:8888/grisgis/rest/services/bdsMap_Public/MapServer/{lid}/query"
    params = {
        'where': '1=1',
        'outFields': '*',
        'f': 'json',
        'outSR': '4326', # Output coordinate system: WGS84
    }
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    print(f"\nFetching features from Layer {lid} ({name})...")
    res = requests.get(url, params=params, headers=headers, verify=False, timeout=30)
    if res.status_code != 200:
        print(f"Failed to fetch Layer {lid}: {res.status_code}")
        return False
        
    data = res.json()
    features = data.get("features", [])
    print(f"Received {len(features)} features.")
    
    geojson_features = []
    for f in features:
        geojson_f = esri_to_geojson(f)
        if geojson_f:
            geojson_features.append(geojson_f)
            
    if not geojson_features:
        print("No valid spatial features converted.")
        return False
        
    geojson_collection = {
        "type": "FeatureCollection",
        "features": geojson_features
    }
    
    # Load into GeoDataFrame
    print("Loading into GeoDataFrame...")
    gdf = gpd.GeoDataFrame.from_features(geojson_collection)
    gdf.set_crs(epsg=4326, inplace=True)
    
    # Save as Shapefile
    # Shapefile files will be created in out_dir
    shp_path = os.path.join(out_dir, f"{name}.shp")
    print(f"Saving Shapefile to {shp_path}...")
    gdf.to_file(shp_path, encoding='cp949') # Save as CP949 for standard Korean GIS software support (QGIS, ArcMap)
    print("Successfully saved Shapefile!")
    return True

def main():
    os.makedirs("scratch/gris_shp", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Fetch and save Layer 11 (도시개발구역)
    fetch_and_save_shp(11, "Gyeonggi_Taekji_Gaebal", "scratch/gris_shp")
    
    # Fetch and save Layer 13 (정비구역)
    fetch_and_save_shp(13, "Gyeonggi_Jeongbi_Guyeok", "scratch/gris_shp")
    
    # Zip up all files
    zip_path = "data/Gyeonggi_GIS_Shapefiles.zip"
    print(f"\nPackaging Shapefiles into {zip_path}...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("scratch/gris_shp"):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, file)
                
    print(f"Zip archive successfully created: {zip_path}")
    print(f"Size: {os.path.getsize(zip_path) / 1024:.2f} KB")

if __name__ == '__main__':
    main()
