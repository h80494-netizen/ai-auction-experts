import requests
import json

lat, lng = 37.5133, 127.1001  # Jamsil Station approx coordinates
query = f"""
[out:json][timeout:5];
(
  way(around:250, {lat}, {lng})["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"];
);
out geom;
"""
url = "https://lz4.overpass-api.de/api/interpreter"
print("Sending Overpass around query...")
response = requests.post(url, data={"data": query}, timeout=5.0)
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    elements = data.get("elements", [])
    print(f"Found {len(elements)} elements.")
    for el in elements[:5]:
        tags = el.get("tags", {})
        print(f" - {el['id']}: name={tags.get('name')}, highway={tags.get('highway')}, geom_len={len(el.get('geometry', []))}")
else:
    print(response.text)
