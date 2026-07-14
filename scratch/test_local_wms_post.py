import requests
import time

url = "http://127.0.0.1:8000/api/gmr/wms"

params = {
    'SERVICE': 'WMS',
    'VERSION': '1.1.1',
    'REQUEST': 'GetMap',
    'FORMAT': 'image/png',
    'TRANSPARENT': 'true',
    'STYLES': '',
    'LAYERS': 'vw_gis_pop_road',
    'VIEWPARAMS': 'stdr:20253;flag:time;val:20;radius:100;',
    'STORE': 'gmr_new',
    'SRS': 'EPSG:3857',
    'WIDTH': '256',
    'HEIGHT': '256',
    'BBOX': '14139800,4474800,14140400,4475400'
}

try:
    print("--- FIRST REQUEST (Cache Miss) ---")
    start = time.time()
    resp = requests.get(url, params=params, timeout=10)
    end = time.time()
    print("Status Code:", resp.status_code)
    print("Content-Type:", resp.headers.get("Content-Type"))
    print("Length of response:", len(resp.content))
    print(f"Time Taken: {end - start:.4f} seconds")
    
    print("\n--- SECOND REQUEST (Cache Hit) ---")
    start = time.time()
    resp = requests.get(url, params=params, timeout=10)
    end = time.time()
    print("Status Code:", resp.status_code)
    print("Content-Type:", resp.headers.get("Content-Type"))
    print("Length of response:", len(resp.content))
    print(f"Time Taken: {end - start:.4f} seconds")
    
except Exception as e:
    print("Error:", e)
