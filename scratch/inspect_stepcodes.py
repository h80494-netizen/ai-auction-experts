import json

with open('public/data/taekji.geojson', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Collect all unique stepCode values
step_codes = set()
for f in data['features']:
    step_codes.add(f['properties'].get('stepCode'))

print("Unique stepCode values in taekji.geojson:", step_codes)

# Attempt to decode the gibberish using latin-1 encoding and then cp949/euc-kr encoding
print("\nAttempting to repair sample gibberish text:")
sample_text = "ÀºÆò±¸ ´ëÁ¶µ¿ 2-9 ¿ª¼¼±Ç Ã»³âÁÖÅÃ(°ø°øÁö¿원¹Î°£ÀÓ´ëÁÖÅÃ) °ø±ÞÃËÁøÁö±¸"
try:
    # Gibberish is often read as ISO-8859-1 (latin1) when it should have been CP949
    bytes_recovered = sample_text.encode('latin1')
    decoded_text = bytes_recovered.decode('cp949')
    print("Decoded successfully:", decoded_text)
except Exception as e:
    print("Failed to decode sample:", e)

# Let's search for Wirye by decoding all zoneName values in the geojson first
print("\nSearching for Wirye features by decoding properties:")
found_count = 0
for idx, feature in enumerate(data['features']):
    props = feature['properties']
    name = props.get('zoneName', '')
    if name:
        try:
            # Try to restore the original cp949 string
            restored = name.encode('latin1').decode('cp949')
            if '위례' in restored:
                print(f"Index: {idx}, Decoded ZoneName: {restored}, Original Properties: {props}")
                found_count += 1
        except Exception:
            pass

print(f"Found {found_count} decoded Wirye features.")
