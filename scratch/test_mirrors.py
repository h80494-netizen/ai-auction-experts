import requests

mirrors = [
    'https://lz4.overpass-api.de/api/interpreter',
    'https://z.overpass-api.de/api/interpreter',
    'https://overpass.kumi.systems/api/interpreter',
    'https://overpass-api.de/api/interpreter'
]

q = """
[out:json][timeout:8];
(
  relation["boundary"="administrative"]["admin_level"~"8|9"]["name"~"^(대치동)$"](37.4,126.8,37.6,127.2);
);
out geom;
"""

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

for url in mirrors:
    try:
        print(f"Testing mirror: {url} ...")
        r = requests.post(url, data={'data': q}, headers=headers, timeout=8)
        print(f"  Status code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"  Success! Found {len(data.get('elements', []))} elements.")
    except Exception as e:
        print(f"  Error: {e}")
