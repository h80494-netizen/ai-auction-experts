import requests
import json

url = "https://gris.gg.go.kr:8888/grisgis/rest/services/bdsMap_Public/MapServer/13/query"
params = {
    'where': '1=1',
    'outFields': '*',
    'f': 'geojson',
    'outSR': '4326',
    'resultRecordCount': '5'
}

headers = {
    'User-Agent': 'Mozilla/5.0'
}

try:
    print(f"Querying layer 13 (정비구역) features...")
    res = requests.get(url, params=params, headers=headers, verify=False, timeout=10)
    print("Status:", res.status_code)
    
    res_json = res.json()
    features = res_json.get("features", [])
    print(f"Number of features returned: {len(features)}")
    if features:
        print("\nFirst feature properties:")
        print(json.dumps(features[0].get("properties"), indent=2, ensure_ascii=False))
        geom = features[0].get("geometry", {})
        print("First feature geometry type:", geom.get("type"))
        print("First feature geometry coordinates (truncated):", str(geom.get("coordinates"))[:200])
except Exception as e:
    print("Error querying layer 13:", e)
