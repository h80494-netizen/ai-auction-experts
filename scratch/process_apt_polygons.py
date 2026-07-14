import json
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

def fetch_parcel(feature):
    props = feature['properties']
    lng, lat = feature['geometry']['coordinates']
    url = f"http://api.vworld.kr/req/data?service=data&request=GetFeature&data=lp_pa_cbnd_bubun&key=2C1B6EA3-A71D-3294-9749-F878465C245B&domain=localhost&geomFilter=POINT({lng} {lat})"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if 'response' in data and 'result' in data['response']:
            fc = data['response']['result']['featureCollection']
            # Take the first polygon from the feature collection
            if fc and 'features' in fc and len(fc['features']) > 0:
                polygon_geom = fc['features'][0]['geometry']
                # Create new feature with polygon geometry and original properties
                new_feature = {
                    "type": "Feature",
                    "geometry": polygon_geom,
                    "properties": props
                }
                return new_feature
    except Exception as e:
        # print(f"Error fetching {props.get('name')}: {e}")
        pass
    
    # If fetch fails, return None
    return None

def main():
    in_path = 'c:/Users/llll/Documents/두인경매/바이브코딩/public/data/apt_info.geojson'
    out_path = 'c:/Users/llll/Documents/두인경매/바이브코딩/public/data/apt_info_500_polygons.geojson'
    
    print(f"Loading {in_path}...")
    with open(in_path, 'r', encoding='utf-8') as f:
        geo = json.load(f)
        
    print("Filtering features with households >= 500...")
    features_to_fetch = [f for f in geo['features'] if f['properties'].get('households', 0) >= 500]
    total = len(features_to_fetch)
    print(f"Total features to fetch: {total}")
    
    start_time = time.time()
    results = []
    
    # Use ThreadPoolExecutor for concurrent requests
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(fetch_parcel, f): f for f in features_to_fetch}
        
        count = 0
        for future in as_completed(futures):
            count += 1
            if count % 100 == 0:
                print(f"Processed {count}/{total}...")
                
            res = future.result()
            if res is not None:
                results.append(res)
                
    success_count = len(results)
    print(f"Successfully fetched {success_count}/{total} polygons in {time.time() - start_time:.2f} seconds.")
    
    # Save the output
    out_geo = {
        "type": "FeatureCollection",
        "features": results
    }
    
    print(f"Saving to {out_path}...")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out_geo, f, ensure_ascii=False)
        
    print("Done!")

if __name__ == '__main__':
    main()
