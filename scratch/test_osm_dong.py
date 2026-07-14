import requests
import json

url = "https://overpass-api.de/api/interpreter"
q = """
[out:json][timeout:15];
(
  relation["boundary"="administrative"]["admin_level"~"8|9"]["name"~"^(대치1동|대치동|잠실동)$"](37.4,126.8,37.6,127.2);
);
out geom;
"""
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

r = requests.post(url, data={'data': q}, headers=headers, timeout=15)
print("Status:", r.status_code)
if r.status_code == 200:
    data = r.json()
    elements = data.get('elements', [])
    print(f"Found {len(elements)} elements")
    for el in elements:
        tags = el.get('tags', {})
        print(f"Type: {el['type']}, ID: {el['id']}, Name: {tags.get('name')}, Name:ko: {tags.get('name:ko')}, admin_level: {tags.get('admin_level')}")
else:
    print(r.text[:300])
