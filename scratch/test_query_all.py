import requests

headers = {
    'User-Agent': 'Mozilla/5.0'
}

for lid in [11, 12, 13, 14, 15]:
    url = f"https://gris.gg.go.kr:8888/grisgis/rest/services/bdsMap_Public/MapServer/{lid}/query"
    params = {
        'where': '1=1',
        'returnCountOnly': 'true',
        'f': 'json'
    }
    try:
        res = requests.get(url, params=params, headers=headers, verify=False, timeout=10)
        data = res.json()
        count = data.get("count", 0)
        print(f"Layer ID: {lid} - Record count in DB: {count}")
    except Exception as e:
        print(f"Error querying Layer {lid}:", e)
