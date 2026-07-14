import requests

url = "https://gris.gg.go.kr:8888/grisgis/rest/services/bdsMap_Public/MapServer/layers?f=json"
headers = {
    'User-Agent': 'Mozilla/5.0'
}

try:
    res = requests.get(url, headers=headers, verify=False, timeout=15)
    data = res.json()
    layers = data.get("layers", [])
    print("bdsMap_Public Layers:")
    for l in layers:
        lid = l.get("id")
        name = l.get("name", "")
        # Print using repr to see the clean Unicode string
        print(f"Layer ID: {lid}, Name: {repr(name)}")
except Exception as e:
    print("Error:", e)
