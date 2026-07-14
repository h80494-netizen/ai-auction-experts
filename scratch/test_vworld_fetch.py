import json
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_parcel(feature):
    lng, lat = feature['geometry']['coordinates']
    url = f"http://api.vworld.kr/req/data?service=data&request=GetFeature&data=lp_pa_cbnd_bubun&key=3A1EB8EB-4521-3F7A-A195-257C0C767D89&domain=http://localhost:8000&geomFilter=POINT({lng} {lat})"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if 'response' in data and 'result' in data['response']:
            return data['response']['result']['featureCollection']
    except Exception:
        pass
    return None

def main():
    with open('c:/Users/llll/Documents/두인경매/바이브코딩/public/data/apt_info.geojson', 'r', encoding='utf-8') as f:
        geo = json.load(f)
    
    features = geo['features'][:100]
    
    start_time = time.time()
    
    results = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(fetch_parcel, f) for f in features]
        for future in as_completed(futures):
            results.append(future.result())
            
    success = sum(1 for r in results if r is not None)
    print(f"Fetched {success}/100 polygons in {time.time() - start_time:.2f} seconds.")

if __name__ == '__main__':
    main()
