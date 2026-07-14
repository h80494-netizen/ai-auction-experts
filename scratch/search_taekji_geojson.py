import json
import os

path = r"c:\Users\llll\Documents\두인경매\바이브코딩\public\data\taekji.geojson"

if not os.path.exists(path):
    print("taekji.geojson not found!")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total features in taekji.geojson: {len(data['features'])}")

found = []
for feature in data['features']:
    props = feature.get('properties', {})
    name = props.get('zoneName', '')
    if '수진' in name or '태평' in name or '성남' in name:
        found.append(props)

print(f"Found {len(found)} matches in taekji.geojson:")
for f in found:
    print(f)
