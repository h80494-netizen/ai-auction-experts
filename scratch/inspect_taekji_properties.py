import json

# Read properties and write to a text file to avoid console encoding issues
geojson_path = 'public/data/taekji.geojson'
with open(geojson_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('scratch/taekji_properties.txt', 'w', encoding='utf-8') as out:
    for i, feature in enumerate(data['features']):
        props = feature.get('properties', {})
        out.write(f"Feature {i}: {json.dumps(props, ensure_ascii=False)}\n")

print("Done writing properties to scratch/taekji_properties.txt")
