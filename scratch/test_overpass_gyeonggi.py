import requests
import json

urls = [
    "https://overpass.private.coffee/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
]

# Seohyeon station area, Bundang
c_min_lat = 37.378
c_max_lat = 37.388
c_min_lng = 127.118
c_max_lng = 127.128

query = f"""
[out:json][timeout:15];
(
  way["highway"]({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng});
);
out geom;
"""

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "http://localhost:8000/",
}

for url in urls:
    print(f"\nQuerying {url} ...")
    try:
        response = requests.post(url, data={"data": query}, headers=headers, timeout=15.0)
        print("Status:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])
            print(f"Success! Found {len(elements)} highway elements.")
            if elements:
                highway_types = {}
                for el in elements:
                    h = el.get("tags", {}).get("highway")
                    highway_types[h] = highway_types.get(h, 0) + 1
                print("Highway types distribution:", highway_types)
        else:
            print("Response content:", response.text[:200])
    except Exception as e:
        print("Failed:", e)
