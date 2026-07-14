import requests
import json

# Query Layer 12 and Layer 13 info
headers = {
    'User-Agent': 'Mozilla/5.0'
}

for lid in [11, 12, 13]:
    url = f"https://gris.gg.go.kr:8888/grisgis/rest/services/bdsMap_Public/MapServer/{lid}?f=json"
    print(f"\n--- Layer {lid} Info ---")
    try:
        res = requests.get(url, headers=headers, verify=False, timeout=10)
        data = res.json()
        print("Name:", data.get("name"))
        print("Type:", data.get("type"))
        print("Max Record Count:", data.get("maxRecordCount"))
        print("Capabilities:", data.get("capabilities"))
        # Print first 5 fields
        fields = data.get("fields", [])
        print(f"Fields ({len(fields)}):")
        for f in fields[:8]:
            print(f"  {f.get('name')} ({f.get('type')}) - {f.get('alias')}")
    except Exception as e:
        print("Error:", e)
