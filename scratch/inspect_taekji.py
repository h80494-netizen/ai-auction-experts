import json
import sys

with open('public/data/taekji.geojson', 'r', encoding='utf-8') as f:
    data = json.load(f)

output = []
output.append(f"Total features: {len(data['features'])}")

if data['features']:
    first_feature = data['features'][0]
    output.append(f"Keys in properties: {list(first_feature['properties'].keys())}")
    
    output.append("\nSample properties from first 5 features:")
    for i in range(min(5, len(data['features']))):
        output.append(f"\nFeature {i}:")
        output.append(json.dumps(data['features'][i]['properties'], ensure_ascii=False, indent=2))

    # Also search for '위례' again, maybe it's under 'zoneName' or other fields
    wirye_features = []
    for idx, feature in enumerate(data['features']):
        props = feature['properties']
        for k, v in props.items():
            if v and '위례' in str(v):
                wirye_features.append((idx, props))
                break
                
    output.append(f"\nFound {len(wirye_features)} Wirye features:")
    for idx, props in wirye_features:
        output.append(f"Feature Index: {idx}")
        output.append(json.dumps(props, ensure_ascii=False, indent=2))

with open('scratch/taekji_inspect.txt', 'w', encoding='utf-8') as out_f:
    out_f.write('\n'.join(output))

print("Inspection completed. Saved to scratch/taekji_inspect.txt")
