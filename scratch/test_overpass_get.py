import requests
import urllib.parse

urls = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter"
]

# Seohyeon station area, Bundang
c_min_lat = 37.378
c_max_lat = 37.388
c_min_lng = 127.118
c_max_lng = 127.128

query = f"""[out:json][timeout:15];(way["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"]({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng}););out geom;"""

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "http://localhost:8000/",
}

for url in urls:
    get_url = f"{url}?data={urllib.parse.quote(query)}"
    print(f"\nQuerying GET {url} ...")
    try:
        response = requests.get(get_url, headers=headers, timeout=15.0)
        print("Status:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])
            print(f"Success! Found {len(elements)} highway elements.")
            if elements:
                break
        else:
            print("Response content:", response.text[:200])
    except Exception as e:
        print("Failed:", e)
