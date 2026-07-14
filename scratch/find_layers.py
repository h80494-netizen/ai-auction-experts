import requests
import json

services = ["bdsMap_Basic", "bdsMap_Public", "bdsMap_Intra_Map"]

headers = {
    'User-Agent': 'Mozilla/5.0'
}

for s_name in services:
    url = f"https://gris.gg.go.kr:8888/grisgis/rest/services/{s_name}/MapServer/layers?f=json"
    print(f"\nScanning service: {s_name}...")
    try:
        res = requests.get(url, headers=headers, verify=False, timeout=15)
        if res.status_code == 200:
            data = res.json()
            layers = data.get("layers", [])
            print(f"Found {len(layers)} layers in {s_name}.")
            for l in layers:
                name = l.get("name", "")
                lid = l.get("id")
                # Search for target keywords
                if any(k in name for k in ['택지', '정비', '개발', '도시재생', '재개발', '재건축']):
                    print(f"  [MATCH] Layer ID: {lid}, Name: {name}")
        else:
            print(f"Failed with status: {res.status_code}")
    except Exception as e:
        print("Error:", e)
