# -*- coding: utf-8 -*-
import pandas as pd
import re
import json
import requests
import urllib.parse
import sys
import os

# Set standard streams to utf-8 if possible
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

rate_path = 'data/특목고진학률.xlsx'
try:
    df_raw = pd.read_excel(rate_path, sheet_name="특목고학군")
    headers = [str(h).strip() for h in df_raw.iloc[0]]
    df_rates = df_raw.iloc[1:].copy()
    df_rates.columns = headers
    
    df_rates['비율'] = pd.to_numeric(df_rates['비율'], errors='coerce')
    elite_df = df_rates[df_rates['비율'] >= 0.30].copy()
    print(f"Loaded {len(elite_df)} elite schools from 특목고진학률.xlsx (rate >= 30%).")
except Exception as e:
    print(f"Error loading rates: {e}")
    sys.exit(1)

# Parse Right-side District Rankings Safely by Column Index (Cols 12 to 18)
try:
    df_groups_data = df_raw.iloc[1:, 12:19].copy()
    df_groups_data.columns = ['학군', '학교수', '인원', '진학률', '1', '2', '3']
    right_side = df_groups_data.drop_duplicates().dropna(subset=['학군'])
    
    # We also need a school-to-rate mapping from left-side table (Col 0: 학교명, Col 8: 비율)
    df_schools_data = df_raw.iloc[1:, [0, 8]].copy()
    df_schools_data.columns = ['학교명', '비율']
    school_to_rate = {}
    for idx, r in df_schools_data.iterrows():
        s_name = str(r['학교명']).strip()
        s_rate = pd.to_numeric(r['비율'], errors='coerce')
        if s_name and not pd.isna(s_rate):
            school_to_rate[s_name] = s_rate
            school_to_rate[s_name.replace('중학교', '').replace('중', '').strip()] = s_rate
            
    # Pre-defined mappings for school to group
    school_to_group = {
        "대원국제중학교": "성동 광진3",
        "영훈국제중학교": "성북 강북1",
        "휘문중학교": "강남 서초2",
        "세화여자중학교": "강남 서초3",
        "신동중학교": "강남 서초3",
        "양정중학교": "강서 양천3",
        "신사중학교": "강남 서초1",
        "경희중학교": "동부1",
        "청심국제중학교": "기타",
        "송산중학교": "기타"
    }
    
    # Pre-defined mappings for Gyeonggi SGGs to group
    sgg_to_group_name = {
        "분당구": "성남2구역",
        "일산동구": "고양2구역",
        "일산서구": "고양2구역",
        "수지구": "용인2구역",
        "연수구": "인천3학교군",
        "과천시": "안양2구역",
        "동안구": "안양1구역",
        "영통구": "수원2구역",
        "가평군": "기타",
        "화성시": "기타"
    }

    # Helper to format rate nicely
    def format_avg_rate(val):
        try:
            val_f = float(val)
            if val_f < 0.1 and val_f > 0:
                return f"{val_f * 100:.2f}%"
            return f"{val_f:.2f}%"
        except:
            return str(val)

    # Build group_info mapping
    group_info = {}
    for idx, r in right_side.iterrows():
        g_name = str(r['학군']).strip()
        avg_rate_val = r['진학률']
        avg_rate = format_avg_rate(avg_rate_val)
        
        top1 = str(r['1']).strip()
        top2 = str(r['2']).strip()
        top3 = str(r['3']).strip()
        
        schools_list = []
        for rank, name in enumerate([top1, top2, top3], 1):
            if name and name != 'nan':
                clean_name = name.replace('중학교', '').replace('중', '').strip()
                rate_val = school_to_rate.get(name) or school_to_rate.get(clean_name) or school_to_rate.get(name + '중학교') or school_to_rate.get(name + '중')
                rate_str = f"{rate_val * 100:.2f}%" if rate_val else "정보 없음"
                schools_list.append({
                    "rank": rank,
                    "name": name if name.endswith('중학교') or name.endswith('중') else name + '중학교',
                    "rate": rate_str
                })
        
        group_info[g_name] = {
            "group_name": g_name,
            "avg_rate": avg_rate,
            "top_schools": schools_list
        }
    print(f"Loaded school group ranking statistics for {len(group_info)} groups.")
except Exception as e:
    print(f"Error parsing group rankings: {e}")
    sys.exit(1)

# 2. Load school districts mapping from 중학교학군.xlsx
school_path = 'data/중학교학군.xlsx'
try:
    df_school = pd.read_excel(school_path, sheet_name="학군별지역")
    print(f"Loaded 중학교학군.xlsx: {len(df_school)} rows.")
except Exception as e:
    print(f"Error loading school districts: {e}")
    sys.exit(1)

# Helper function to expand dong list in Column 6 (해당지역)
def expand_dong_string(dong_str):
    parts = re.split(r'[,/\s]+', str(dong_str))
    expanded = []
    for p in parts:
        p = p.strip()
        if not p or p == 'nan':
            continue
        p = re.sub(r'\(.*?\)', '', p)
        p = re.sub(r'\d+통~?\d*통', '', p)
        p = p.strip()
        if not p:
            continue
        
        # Avoid matching group names as dongs
        if p in ['동구', '연수구', '일산동구', '일산서구', '분당구', '수지구', '과천시', '안양시', '성남시', '자치구별', '해당지역']:
            continue
            
        m = re.match(r'^([^\d,]+)(\d+(?:,\d+)*)동$', p)
        if m:
            base = m.group(1)
            nums = m.group(2).split(',')
            for num in nums:
                expanded.append(f"{base}{num}동")
            continue
            
        if not p.endswith('동') and not p.endswith('가') and not p.endswith('로'):
            expanded.append(p + '동')
        else:
            expanded.append(p)
    return expanded

# Helper to find school assignable dongs for Seoul
def find_seoul_school_dongs(school_name):
    base_name = school_name.replace('중학교', '').replace('중', '').strip()
    
    # Search in df_school Col 2, Col 3, Col 4
    for idx, row in df_school.iterrows():
        col2 = str(row.iloc[2])
        col3 = str(row.iloc[3])
        col4 = str(row.iloc[4])
        
        if base_name in col2 or base_name in col3 or base_name in col4:
            dongs_str = str(row.iloc[6])
            if dongs_str and dongs_str != 'nan':
                return expand_dong_string(dongs_str)
    return []

# Build dong to schools mapping (Seoul) and SGG to schools mapping (Gyeonggi/Incheon)
dong_to_schools = {}
sgg_to_schools = {}

for idx, row in elite_df.iterrows():
    name = str(row['학교명']).strip()
    address = str(row['주소']).strip()
    
    is_seoul = '서울' in address
    is_incheon = '인천' in address
    is_gyeonggi = '경기' in address or (not is_seoul and not is_incheon)
    
    if is_seoul:
        dongs = find_seoul_school_dongs(name)
        if not dongs:
            m = re.search(r'\s([가-힣\d]+동)\s?', address)
            if m:
                dongs = [m.group(1)]
        for d in dongs:
            if d not in dong_to_schools:
                dong_to_schools[d] = []
            if name not in dong_to_schools[d]:
                dong_to_schools[d].append(name)
    else:
        tokens = address.split()
        sgg = ""
        for t in tokens:
            if t.endswith('구') or t.endswith('군') or t.endswith('시'):
                if t not in ['경기도', '인천광역시', '인천시', '경북도', '충북도', '전북도']:
                    sgg = t
                    break
        if not sgg:
            sgg = str(row['지역']).strip()
        
        sgg_tokens = sgg.split()
        if sgg_tokens:
            sgg = sgg_tokens[-1]
            
        if sgg:
            if sgg not in sgg_to_schools:
                sgg_to_schools[sgg] = []
            if name not in sgg_to_schools[sgg]:
                sgg_to_schools[sgg].append(name)

print(f"Total mapped unique Seoul dongs: {len(dong_to_schools)}")
print(f"Total mapped unique Gyeonggi/Incheon SGGs: {len(sgg_to_schools)}")

# 3. Download and merge HangJeongDong GeoJSON
base_url = "https://raw.githubusercontent.com/raqoon886/Local_HangJeongDong/master/"
regions = ["서울특별시", "인천광역시", "경기도"]
geojson_features = []

for reg in regions:
    filename = f"hangjeongdong_{reg}.geojson"
    url = base_url + urllib.parse.quote(filename)
    print(f"Downloading {filename}...")
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            data = r.json()
            feats = data.get('features', [])
            print(f"  Loaded {len(feats)} features.")
            for f in feats:
                f['properties']['region'] = reg
                geojson_features.append(f)
        else:
            print(f"  Error: HTTP {r.status_code}")
    except Exception as e:
        print(f"  Exception: {e}")

print(f"Total downloaded features: {len(geojson_features)}")

# 4. Group and compile features
compiled_features = []
grouped_regions = {}

for feat in geojson_features:
    props = feat['properties']
    adm_nm = str(props.get('adm_nm', ''))
    sido = str(props.get('sidonm', ''))
    sgg = str(props.get('sggnm', ''))
    dong = adm_nm.split()[-1] if adm_nm.split() else ""
    reg = props.get('region', '')
    
    if sido == "서울특별시":
        matching_schools = []
        for d_name, schools in dong_to_schools.items():
            if dong == d_name or (d_name.endswith('동') and dong.startswith(d_name[:-1])):
                matching_schools.extend(schools)
        
        if matching_schools:
            matching_schools = list(set(matching_schools))
            group_key = f"seoul_{adm_nm}"
            if group_key not in grouped_regions:
                grouped_regions[group_key] = {
                    "dong_name": dong,
                    "sido_name": sido,
                    "sgg_name": sgg,
                    "level": "dong",
                    "school_districts": set(),
                    "polygons": []
                }
            grouped_regions[group_key]["school_districts"].update(matching_schools)
            
            geom = feat['geometry']
            if geom['type'] == 'Polygon':
                grouped_regions[group_key]["polygons"].append(geom['coordinates'])
            elif geom['type'] == 'MultiPolygon':
                for poly in geom['coordinates']:
                    grouped_regions[group_key]["polygons"].append(poly)
    else:
        matching_schools = []
        for sgg_name, schools in sgg_to_schools.items():
            if sgg == sgg_name or sgg_name in sgg or sgg in sgg_name:
                matching_schools.extend(schools)
                
        if matching_schools:
            matching_schools = list(set(matching_schools))
            group_key = f"sgg_{sido}_{sgg}"
            if group_key not in grouped_regions:
                grouped_regions[group_key] = {
                    "dong_name": sgg,
                    "sido_name": sido,
                    "sgg_name": sgg,
                    "level": "sgg",
                    "school_districts": set(),
                    "polygons": []
                }
            grouped_regions[group_key]["school_districts"].update(matching_schools)
            
            geom = feat['geometry']
            if geom['type'] == 'Polygon':
                grouped_regions[group_key]["polygons"].append(geom['coordinates'])
            elif geom['type'] == 'MultiPolygon':
                for poly in geom['coordinates']:
                    grouped_regions[group_key]["polygons"].append(poly)

# Build GeoJSON features from grouped regions and embed enriched statistics
for key, info in grouped_regions.items():
    if not info["polygons"]:
        continue
        
    school_districts_list = list(info["school_districts"])
    
    # Resolve School Group Name and Top Schools Statistics
    target_group_name = None
    group_stats = None
    
    if info["level"] == "dong":
        for sch in school_districts_list:
            g_name = school_to_group.get(sch) or school_to_group.get(sch + '중학교')
            if g_name:
                target_group_name = g_name
                break
    else:
        clean_sgg = info["sgg_name"]
        for k_sgg, g_name in sgg_to_group_name.items():
            if k_sgg in clean_sgg or clean_sgg in k_sgg:
                target_group_name = g_name
                break
                
    if target_group_name and target_group_name in group_info:
        group_stats = group_info[target_group_name]
        
    new_feat = {
        "type": "Feature",
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": info["polygons"]
        },
        "properties": {
            "dong_name": info["dong_name"],
            "sido_name": info["sido_name"],
            "sgg_name": info["sgg_name"],
            "level": info["level"],
            "school_districts": school_districts_list,
            "school_group": group_stats["group_name"] if group_stats else (target_group_name or "우수학군"),
            "group_avg_rate": group_stats["avg_rate"] if group_stats else "정보 없음",
            "top_schools": group_stats["top_schools"] if group_stats else []
        }
    }
    compiled_features.append(new_feat)

print(f"Compiled {len(compiled_features)} enriched school districts boundaries.")

# Save output
output_path = 'public/data/elite_school_dongs.geojson'
os.makedirs(os.path.dirname(output_path), exist_ok=True)

geojson_output = {
    "type": "FeatureCollection",
    "features": compiled_features
}

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(geojson_output, f, ensure_ascii=False, indent=2)

print(f"Successfully saved compiled elite school districts to {output_path} (size: {os.path.getsize(output_path)} bytes).")
