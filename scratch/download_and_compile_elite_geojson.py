# -*- coding: utf-8 -*-
import pandas as pd
import re
import json
import requests
import urllib.parse
import sys

# Set standard streams to utf-8 if possible
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 1. Load Excel mapping
excel_path = 'data/명문중배정행정동.xlsx'
try:
    df = pd.read_excel(excel_path)
    print(f"Loaded Excel: {len(df)} rows.")
except Exception as e:
    print(f"Error loading Excel: {e}")
    sys.exit(1)

# Function to parse and expand dong string
def expand_dong_string(dong_str):
    # Split by comma, slash, space
    parts = re.split(r'[,/\s]+', dong_str)
    expanded = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        
        # Remove parenthesized notes like (15통, 32~37통) or 1통~16통
        p = re.sub(r'\(.*?\)', '', p)
        p = re.sub(r'\d+통~?\d*통', '', p)
        p = p.strip()
        if not p:
            continue
            
        # Ignore regional headers or general region names
        if p in ['동구', '연수구', '일산동구', '일산서구', '분당구', '수지구', '과천시', '안양시', '성남시']:
            continue
            
        # Match pattern like "행당1,2동" or "금호1,2가동"
        m = re.match(r'^([^\d,]+)(\d+(?:,\d+)*)동$', p)
        if m:
            base = m.group(1) # "행당"
            nums = m.group(2).split(',') # ["1", "2"]
            for num in nums:
                expanded.append(f"{base}{num}동")
            continue
            
        # If it doesn't end with '동', check if we need to append '동'
        if not p.endswith('동'):
            if p.endswith('가') or p.endswith('로') or p.endswith('동1') or p.endswith('동2') or p.endswith('동3'):
                expanded.append(p + '동')
            else:
                m2 = re.search(r'\d+$', p)
                if m2:
                    expanded.append(p + '동')
                else:
                    expanded.append(p + '동')
        else:
            expanded.append(p)
    return expanded

# Parse excel rows into a dictionary of {cleaned_dong: [districts]}
dong_to_districts = {}
for idx, row in df.iterrows():
    district = str(row['학군']).strip()
    dong_str = str(row['해당동'])
    dongs = expand_dong_string(dong_str)
    for d in dongs:
        if d not in dong_to_districts:
            dong_to_districts[d] = []
        if district not in dong_to_districts[d]:
            dong_to_districts[d].append(district)

print(f"Total parsed unique dongs from Excel: {len(dong_to_districts)}")

# 2. Download raw GeoJSON files from raqoon886 repository
base_url = "https://raw.githubusercontent.com/raqoon886/Local_HangJeongDong/master/"
regions = ["서울특별시", "인천광역시", "경기도"]
geojson_features = []

for reg in regions:
    filename = f"hangjeongdong_{reg}.geojson"
    url = base_url + urllib.parse.quote(filename)
    print(f"Downloading {filename}...")
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            feats = data.get('features', [])
            print(f"  Successfully loaded {len(feats)} features.")
            for f in feats:
                f['properties']['region'] = reg
                geojson_features.append(f)
        else:
            print(f"  Error downloading {filename}: Status {r.status_code}")
    except Exception as e:
        print(f"  Exception downloading {filename}: {e}")

print(f"Total features downloaded: {len(geojson_features)}")

# 3. Match GeoJSON features to our Excel dongs
matched_features = []
matched_dongs_set = set()

for feat in geojson_features:
    props = feat['properties']
    adm_nm = props.get('adm_nm', '') # e.g. '서울특별시 종로구 사직동'
    tokens = adm_nm.split()
    if not tokens:
        continue
    feat_dong = tokens[-1] # '사직동'
    sido = props.get('sidonm', '') # '서울특별시'
    sgg = props.get('sggnm', '') # '종로구'
    reg = props.get('region', '')
    
    # Let's try matching this feature to any excel dong
    matching_districts = []
    excel_matched_names = []
    
    for ex_dong, districts in dong_to_districts.items():
        match = False
        
        # 1. Exact match
        if feat_dong == ex_dong:
            match = True
        # 2. Special cases for unified/sub-dongs first
        elif '금호2가' in ex_dong or '금호3가' in ex_dong:
            if feat_dong == '금호2·3가동':
                match = True
        elif '성수동1가' in ex_dong or '성수1가' in ex_dong:
            if feat_dong.startswith('성수1가'):
                match = True
        elif '성수동2가' in ex_dong or '성수2가' in ex_dong:
            if feat_dong.startswith('성수2가'):
                match = True
        elif '왕십리' in ex_dong:
            if '왕십리' in feat_dong:
                match = True
        # 3. If ex_dong is '대치동' and feat_dong is '대치1동' or '대치2동'
        elif ex_dong.endswith('동') and len(ex_dong) > 1:
            base_name = ex_dong[:-1] # '대치'
            if feat_dong.startswith(base_name) and feat_dong.endswith('동'):
                match = True
                
        if match:
            # Let's apply regional check to avoid false positives (e.g. 신사동 in Gangnam vs Eunpyeong vs Gwanak)
            is_valid_region = False
            for d in districts:
                # City check
                if "인천" in d and reg == "인천광역시":
                    is_valid_region = True
                elif ("고양" in d or "성남" in d or "용인" in d or "안양" in d or "과천" in d) and reg == "경기도":
                    if "고양" in d and "고양시" in adm_nm:
                        is_valid_region = True
                    elif "성남" in d and "성남시" in adm_nm:
                        is_valid_region = True
                    elif "용인" in d and "용인시" in adm_nm:
                        is_valid_region = True
                    elif "안양" in d and "안양시" in adm_nm:
                        is_valid_region = True
                    elif "과천" in d and "과천시" in adm_nm:
                        is_valid_region = True
                    else:
                        is_valid_region = True
                elif reg == "서울특별시" and not any(k in d for k in ["인천", "고양", "성남", "용인", "안양", "과천"]):
                    if "강남" in d and ("강남구" in sgg or "서초구" in sgg):
                        is_valid_region = True
                    elif "서초" in d and ("강남구" in sgg or "서초구" in sgg):
                        is_valid_region = True
                    elif "강동" in d and ("강동구" in sgg or "송파구" in sgg):
                        is_valid_region = True
                    elif "송파" in d and ("강동구" in sgg or "송파구" in sgg):
                        is_valid_region = True
                    elif "강서" in d and ("강서구" in sgg or "양천구" in sgg):
                        is_valid_region = True
                    elif "양천" in d and ("강서구" in sgg or "양천구" in sgg):
                        is_valid_region = True
                    elif "성북" in d and ("성북구" in sgg or "강북구" in sgg):
                        is_valid_region = True
                    elif "강북" in d and ("성북구" in sgg or "강북구" in sgg):
                        is_valid_region = True
                    elif "성동" in d and ("성동구" in sgg or "광진구" in sgg):
                        is_valid_region = True
                    elif "광진" in d and ("성동구" in sgg or "광진구" in sgg):
                        is_valid_region = True
                    elif "동부" in d and ("동대문구" in sgg or "중랑구" in sgg):
                        is_valid_region = True
                    elif "중부" in d and ("종로구" in sgg or "중구" in sgg or "용산구" in sgg):
                        is_valid_region = True
                    elif "서부" in d and ("서대문구" in sgg or "마포구" in sgg or "은평구" in sgg):
                        is_valid_region = True
                    else:
                        is_valid_region = True
                        
            if is_valid_region:
                for d in districts:
                    if d not in matching_districts:
                        matching_districts.append(d)
                if ex_dong not in excel_matched_names:
                    excel_matched_names.append(ex_dong)
                    
    if matching_districts:
        new_feat = {
            "type": "Feature",
            "geometry": feat["geometry"],
            "properties": {
                "dong_name": feat_dong,
                "sido_name": sido,
                "sgg_name": sgg,
                "full_name": adm_nm,
                "school_districts": matching_districts
            }
        }
        matched_features.append(new_feat)
        for name in excel_matched_names:
            matched_dongs_set.add(name)

# 4. Group features: Seoul as dong, Gyeonggi/Incheon as SGG (Si/Gu) level
grouped_features = {}
for feat in matched_features:
    props = feat["properties"]
    sido = props["sido_name"]
    sgg = props["sgg_name"]
    dong = props["dong_name"]
    full = props["full_name"]
    
    if sido == "서울특별시":
        group_key = f"seoul_{full}"
        display_name = dong
        level = "dong"
    else:
        group_key = f"metro_{sido}_{sgg}"
        display_name = sgg
        level = "sgg"
        
    if group_key not in grouped_features:
        grouped_features[group_key] = {
            "sido_name": sido,
            "sgg_name": sgg,
            "display_name": display_name,
            "level": level,
            "school_districts": set(),
            "polygons": []
        }
        
    for d in props["school_districts"]:
        grouped_features[group_key]["school_districts"].add(d)
        
    geom = feat["geometry"]
    if geom["type"] == "Polygon":
        grouped_features[group_key]["polygons"].append(geom["coordinates"])
    elif geom["type"] == "MultiPolygon":
        for poly in geom["coordinates"]:
            grouped_features[group_key]["polygons"].append(poly)

compiled_features = []
for key, info in grouped_features.items():
    if not info["polygons"]:
        continue
        
    new_feat = {
        "type": "Feature",
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": info["polygons"]
        },
        "properties": {
            "dong_name": info["display_name"],
            "sido_name": info["sido_name"],
            "sgg_name": info["sgg_name"],
            "level": info["level"],
            "school_districts": list(info["school_districts"])
        }
    }
    compiled_features.append(new_feat)

matched_features = compiled_features

# 5. Print stats and identify unmatched dongs from Excel
print(f"\nCompiled {len(matched_features)} matching administrative regions.")
unmatched_dongs = sorted([d for d in dong_to_districts.keys() if d not in matched_dongs_set])
print(f"Unmatched dongs count from Excel: {len(unmatched_dongs)}")
print("Unmatched dongs list:", unmatched_dongs)

# Save output
output_path = 'public/data/elite_school_dongs.geojson'
geojson_output = {
    "type": "FeatureCollection",
    "features": matched_features
}

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(geojson_output, f, ensure_ascii=False, indent=2)

print(f"\nSuccessfully compiled elite school dongs GeoJSON! Saved {len(matched_features)} features to {output_path}")

