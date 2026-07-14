import requests
import json

# ArcGIS REST directory URL
# Standard format takes f=json to return service list in JSON format
url = "https://gris.gg.go.kr:8888/grisgis/rest/services/?f=json"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36'
}

try:
    print(f"Querying GRIS ArcGIS services directory: {url}...")
    res = requests.get(url, headers=headers, verify=False, timeout=15)
    print("Status:", res.status_code)
    print("Content-Type:", res.headers.get("Content-Type"))
    
    try:
        res_json = res.json()
        print("ArcGIS Services JSON successfully loaded!")
        print(json.dumps(res_json, indent=2, ensure_ascii=False)[:3000])
    except Exception as je:
        print("JSON parsing failed. Printing first 1000 characters of raw text:")
        print(res.text[:1000])
except Exception as e:
    print("Error querying ArcGIS directory:", e)
