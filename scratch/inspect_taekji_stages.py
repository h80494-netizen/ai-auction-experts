import json
from collections import Counter

# Load the taekji.geojson and print counts of stepCode/zoneCode
geojson_path = 'public/data/taekji.geojson'
with open(geojson_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total features: {len(data['features'])}")

step_codes = []
zone_codes = []
zone_cds = []

for feature in data['features']:
    props = feature.get('properties', {})
    step_codes.append(props.get('stepCode'))
    zone_codes.append(props.get('zoneCode'))
    zone_cds.append(props.get('zone_cd'))

print("\n--- stepCode Counter ---")
print(Counter(step_codes).most_common(20))

print("\n--- zoneCode Counter ---")
print(Counter(zone_codes).most_common(20))

print("\n--- zone_cd Counter ---")
print(Counter(zone_cds).most_common(20))

print("\n--- Sample properties ---")
for i, f in enumerate(data['features'][:5]):
    print(f"Feature {i}: {f.get('properties')}")
