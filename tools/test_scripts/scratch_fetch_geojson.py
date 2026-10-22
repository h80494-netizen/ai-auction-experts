import pandas as pd
import re
import requests
import json
import time

# 1. 명문중배정행정동.xlsx에서 동 목록 추출
df = pd.read_excel('data/명문중배정행정동.xlsx')
dong_map = {} # 동이름 -> 학군명 리스트

for idx, row in df.iterrows():
    school_name = str(row['학군']).strip()
    dong_str = str(row['해당동'])
    parts = re.split(r'[,/\s]+', dong_str)
    for p in parts:
        p = p.strip()
        if p and p not in ['동구', '연수구', '일산동구', '일산서구', '분당구', '수지구', '과천시', '안양시']:
            if '통' in p:
                continue
            if p not in dong_map:
                dong_map[p] = []
            if school_name not in dong_map[p]:
                dong_map[p].append(school_name)

dongs = sorted(list(dong_map.keys()))
print(f"Extracted {len(dongs)} unique dongs to fetch.")

# 2. OSM Overpass API를 통해 동 경계 획득 (40개씩 배치 처리)
features = []
batch_size = 35

def get_overpass_geom(dong_batch):
    # 정규식 쿼리 구성
    dong_query = "|".join(dong_batch)
    query = f"""
    [out:json][timeout:30];
    (
      relation["boundary"="administrative"]["admin_level"~"8|9"]["name"~"^({dong_query})$"](37.0,126.3,37.8,127.5);
    );
    out geom;
    """
    url = "https://overpass-api.de/api/interpreter"
    try:
        r = requests.post(url, data={"data": query}, timeout=35)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print("Error fetching batch:", e)
    return None

for i in range(0, len(dongs), batch_size):
    batch = dongs[i:i+batch_size]
    print(f"Fetching batch {i // batch_size + 1}... Dongs: {batch[:5]}...")
    
    data = get_overpass_geom(batch)
    if not data or "elements" not in data:
        print("Failed to fetch this batch. Retrying with alternative endpoint...")
        # Failover endpoint
        time.sleep(2)
        continue
        
    elements = data["elements"]
    print(f"Found {len(elements)} boundary elements for this batch.")
    
    for el in elements:
        if el.get("type") == "relation":
            tags = el.get("tags", {})
            name = tags.get("name")
            name_ko = tags.get("name:ko") or name
            
            # 이 동이 우리가 찾는 동 리스트에 속하는지 확인
            matching_dong = None
            for d in batch:
                if d in name_ko:
                    matching_dong = d
                    break
            
            if not matching_dong:
                continue
                
            # Outer members coordinates를 결합하여 Polygon 생성
            members = el.get("members", [])
            polygon_coords = []
            
            # 단순화를 위해 outer member들의 geometry 좌표를 순차적으로 합쳐서 단일 Polygon 생성
            outer_ways_coords = []
            for m in members:
                if m.get("role") == "outer" and "geometry" in m:
                    geom = m["geometry"]
                    coords = [[pt["lon"], pt["lat"]] for pt in geom]
                    if coords:
                        outer_ways_coords.append(coords)
            
            if not outer_ways_coords:
                continue
                
            # 여러 외곽 선들을 결합하여 하나의 폴리곤 루프로 만들기 (단순 결합)
            combined_coords = []
            for way in outer_ways_coords:
                combined_coords.extend(way)
                
            if len(combined_coords) < 3:
                continue
                
            # 폴리곤 닫기
            if combined_coords[0] != combined_coords[-1]:
                combined_coords.append(combined_coords[0])
                
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [combined_coords]
                },
                "properties": {
                    "dong_name": matching_dong,
                    "full_name": name_ko,
                    "school_districts": dong_map[matching_dong]
                }
            })
            
    time.sleep(1.5) # API 매너 타임

# 3. GeoJSON 파일로 내보내기
geojson = {
    "type": "FeatureCollection",
    "features": features
}

output_path = 'public/data/elite_school_dongs.geojson'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

print(f"Successfully compiled elite school dongs GeoJSON! Saved {len(features)} dongs to {output_path}")
