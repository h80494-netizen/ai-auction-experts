import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0'
}

for lid, name in [(11, '도시개발구역'), (13, '정비구역')]:
    url = f"https://gris.gg.go.kr:8888/grisgis/rest/services/bdsMap_Public/MapServer/{lid}/query"
    params = {
        'where': '1=1',
        'outFields': '*',
        'f': 'geojson',
        'outSR': '4326',
        'resultRecordCount': '5'
    }
    try:
        print(f"\nTesting GeoJSON query for Layer {lid} ({name})...")
        res = requests.get(url, params=params, headers=headers, verify=False, timeout=10)
        data = res.json()
        features = data.get("features", [])
        print(f"Features count: {len(features)}")
        if features:
            print("Successfully loaded GeoJSON!")
            print("Sample properties:", features[0].get("properties"))
            print("Geometry Type:", features[0].get("geometry", {}).get("type"))
    except Exception as e:
        print("Error:", e)
