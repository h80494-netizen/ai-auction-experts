import json
import os

path = r"c:\Users\llll\Documents\두인경매\바이브코딩\public\data\taekji.geojson"

if not os.path.exists(path):
    print("taekji.geojson not found!")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total features: {len(data['features'])}")

for feature in data['features'][:15]:
    props = feature.get('properties', {})
    name = props.get('zoneName', '')
    # Check if name has replacement char
    print(f"zoneCode: {props.get('zoneCode')} | name: {name} | repr: {repr(name)}")
