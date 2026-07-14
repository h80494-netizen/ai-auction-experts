import requests
import json

# Let's try querying Gyeonggi Redevelopment zones layer (Layer ID: 12)
# outFields=* to fetch all properties, f=geojson to get GeoJSON output, where=1=1 to get all records
url = "https://gris.gg.go.kr:8888/grisgis/rest/services/bdsMap_Public/MapServer/12/query"
params = {
    'where': '1=1',
    'outFields': '*',
    'f': 'geojson',
    'outSR': '4326', # Force coordinates to WGS84 (lat/lng)
    'resultRecordCount': '5' # Query only 5 features as a test
}

headers = {
    'User-Agent': 'Mozilla/5.0'
}

try:
    print(f"Querying layer 12 features from {url}...")
    res = requests.get(url, params=params, headers=headers, verify=False, timeout=15)
    print("Status:", res.status_code)
    print("Content-Type:", res.headers.get("Content-Type"))
    
    try:
        res_json = res.json()
        print("Successfully fetched features in GeoJSON format!")
        features = res_json.get("features", [])
        print(f"Number of features returned: {len(features)}")
        if features:
            print("First feature metadata:")
            print(json.dumps(features[0].get("properties"), indent=2, ensure_ascii=False))
            print("First feature geometry type:", features[0].get("geometry", {}).get("type"))
            print("First feature coordinate count:", len(features[0].get("geometry", {}).get("coordinates", [[]])[0]))
    except Exception as je:
        print("Failed to parse JSON. Raw output (truncated):")
        print(res.text[:1000])
except Exception as e:
    print("Error querying layer:", e)
