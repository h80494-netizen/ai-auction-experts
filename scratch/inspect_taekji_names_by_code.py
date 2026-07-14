import json

with open('public/data/taekji.geojson', 'r', encoding='utf-8') as f:
    data = json.load(f)

grouped = {}
for f in data['features']:
    props = f['properties']
    step_code = props.get('stepCode', 'NONE')
    zone_name = props.get('zoneName', '')
    zone_code = props.get('zoneCode', '')
    
    # Try to decode the broken name
    try:
        decoded_name = zone_name.encode('latin1').decode('cp949')
    except Exception:
        decoded_name = zone_name # Fallback
        
    if step_code not in grouped:
        grouped[step_code] = []
    grouped[step_code].append((zone_code, decoded_name))

with open('scratch/taekji_stages_decoded.txt', 'w', encoding='utf-8') as out_f:
    for code, items in grouped.items():
        out_f.write(f"\n=========================================\n")
        out_f.write(f"  Step Code: {code} (Total: {len(items)})\n")
        out_f.write(f"=========================================\n")
        # Print first 20 items for each code
        for z_code, name in items[:20]:
            out_f.write(f"ZoneCode: {z_code} | Decoded Name: {name}\n")
            
print("Completed. Output written to scratch/taekji_stages_decoded.txt")
