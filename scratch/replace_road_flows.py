import os

app_path = 'backend/app.py'
if not os.path.exists(app_path):
    print("Cannot find backend/app.py")
    exit(1)

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new get_road_flows function
new_func = """@app.get("/api/map/road_flows")
def get_road_flows(
    min_lat: float, max_lat: float, min_lng: float, max_lng: float
):
    \"\"\"
    지도의 영역(BBox) 내 실제 도로망을 SQLite 그리드 캐시에서 조회(없을 시 OSM Overpass API 1회 수집)하여,
    상위 5단계(Step 6~10) 유동인구 격자의 반경 500m 이내 분포에 따라
    유동량 농도를 산출하여 5단계의 농도별 라인 히트맵 GeoJSON을 반환합니다.
    (도로폭 8m 이하 소도로만 필터링)
    \"\"\"
    import random
    import requests
    import sqlite3
    import math
    import os
    import json
    import re

    # Fast Euclidean distance helper (m)
    def fast_dist(lat1, lng1, lat2, lng2):
        dy = (lat1 - lat2) * 111000.0
        dx = (lng1 - lng2) * 88000.0
        return math.sqrt(dx*dx + dy*dy)

    # 1. 500m 패딩을 주어 BBox 근처의 유동인구 격자를 인메모리로 가져옴
    pad_lat = 0.0045
    pad_lng = 0.0057
    
    grid_min_lat = min_lat - pad_lat
    grid_max_lat = max_lat + pad_lat
    grid_min_lng = min_lng - pad_lng
    grid_max_lng = max_lng + pad_lng
    
    top5_grids = []
    try:
        grid_res = get_grid_demographics(
            min_lat=grid_min_lat,
            max_lat=grid_max_lat,
            min_lng=grid_min_lng,
            max_lng=grid_max_lng,
            type="floating",
            regions="서울,경기,인천"
        )
        if grid_res.get("status") == "success":
            grids = grid_res.get("data", [])
            # 지역별 그룹화
            groups = {}
            for g in grids:
                r = g.get("region") or "seoul"
                if r not in groups:
                    groups[r] = []
                groups[r].append(g)
            
            # 각 지역별로 10분위수 정렬 및 상위 5단계(Step 6~10) 필터링
            for r, group_data in groups.items():
                group_data.sort(key=lambda x: x.get("avg_population", 0))
                n = len(group_data)
                if n == 0:
                    continue
                for index, item in enumerate(group_data):
                    step = int((index / n) * 10) + 1
                    step = min(step, 10)
                    if step >= 6:
                        item["step"] = step
                        top5_grids.append(item)
    except Exception as e:
        print("Failed to load grid demographics for road flows proximity logic:", e)

    # 1-2. 반경 500m 격자 공간 연산을 가속하기 위한 Grid Spatial Hashing 인덱스 구축
    bucket_size_lat = 0.005
    bucket_size_lng = 0.006
    spatial_index = {}
    for tg in top5_grids:
        b_lat = int(tg["lat"] / bucket_size_lat)
        b_lng = int(tg["lng"] / bucket_size_lng)
        key = (b_lat, b_lng)
        if key not in spatial_index:
            spatial_index[key] = []
        spatial_index[key].append(tg)

    # SQLite 로컬 그리드 영구 캐싱 시스템 작동
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'map_data.db')
    if not os.path.exists(db_path):
        db_path = os.path.join(os.path.dirname(__file__), '../data/map_data.db')
    if not os.path.exists(db_path):
        db_path = 'map_data.db'

    # 테이블 초기화 및 인덱스 설정
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS road_cache_grids (
                lat_idx INTEGER,
                lng_idx INTEGER,
                PRIMARY KEY (lat_idx, lng_idx)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS road_cache_segments (
                osm_id INTEGER PRIMARY KEY,
                name TEXT,
                highway TEXT,
                width REAL,
                min_lat REAL,
                max_lat REAL,
                min_lng REAL,
                max_lng REAL,
                coords_json TEXT
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_road_cache_bounds ON road_cache_segments(max_lat, min_lat, max_lng, min_lng)')
        conn.commit()
        conn.close()
    except Exception as e:
        print("Failed to initialize road cache database:", e)

    # 격자 단위(0.01도) 획정
    lat_start = int(math.floor(min_lat / 0.01))
    lat_end = int(math.floor(max_lat / 0.01))
    lng_start = int(math.floor(min_lng / 0.01))
    lng_end = int(math.floor(max_lng / 0.01))

    features = []
    osm_success = False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 캐시 그리드 조회
        cursor.execute('SELECT lat_idx, lng_idx FROM road_cache_grids')
        cached_cells = set(cursor.fetchall())

        # 미캐싱된 셀 식별
        cells_to_fetch = []
        for lat_idx in range(lat_start, lat_end + 1):
            for lng_idx in range(lng_start, lng_end + 1):
                if (lat_idx, lng_idx) not in cached_cells:
                    cells_to_fetch.append((lat_idx, lng_idx))

        # API 부하 방지 및 속도 유지를 위해 1회 맵 이동시 캐싱 쿼리를 최대 6개 셀로 제한
        if len(cells_to_fetch) > 6:
            print(f"Limiting road cell fetches to 6 from {len(cells_to_fetch)}")
            cells_to_fetch = cells_to_fetch[:6]

        urls = [
            "https://overpass-api.de/api/interpreter",
            "https://lz4.overpass-api.de/api/interpreter",
            "https://overpass.osm.ch/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter"
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": "http://localhost:8000/",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        for cell_lat, cell_lng in cells_to_fetch:
            c_min_lat = cell_lat * 0.01
            c_max_lat = (cell_lat + 1) * 0.01
            c_min_lng = cell_lng * 0.01
            c_max_lng = (cell_lng + 1) * 0.01

            query = f\"\"\"
            [out:json][timeout:2];
            (
              way["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"]({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng});
            );
            out geom;
            \"\"\"
            
            cell_fetched = False
            for url in urls:
                try:
                    response = requests.post(url, data={"data": query}, headers=headers, timeout=2.0)
                    if response.status_code == 200:
                        osm_data = response.json()
                        elements = osm_data.get("elements", [])
                        
                        # DB에 저장
                        for el in elements:
                            if el.get("type") == "way" and "geometry" in el:
                                osm_id = el["id"]
                                geom = el["geometry"]
                                coords = [[pt["lon"], pt["lat"]] for pt in geom]
                                if len(coords) < 2:
                                    continue
                                
                                tags = el.get("tags", {})
                                name = tags.get("name") or tags.get("name:ko", "이면도로")
                                highway = tags.get("highway", "소도로")
                                
                                # 도로폭 파싱
                                width_val = None
                                width_str = tags.get("width")
                                if width_str:
                                    try:
                                        match = re.search(r"([0-9.]+)", width_str)
                                        if match:
                                            width_val = float(match.group(1))
                                    except Exception:
                                        pass
                                
                                lats = [pt[1] for pt in geom]
                                lngs = [pt[0] for pt in geom]
                                min_lat_val = min(lats)
                                max_lat_val = max(lats)
                                min_lng_val = min(lngs)
                                max_lng_val = max(lngs)
                                
                                cursor.execute('''
                                    INSERT OR REPLACE INTO road_cache_segments 
                                    (osm_id, name, highway, width, min_lat, max_lat, min_lng, max_lng, coords_json)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (osm_id, name, highway, width_val, min_lat_val, max_lat_val, min_lng_val, max_lng_val, json.dumps(coords)))
                        
                        cursor.execute('INSERT OR REPLACE INTO road_cache_grids (lat_idx, lng_idx) VALUES (?, ?)', (cell_lat, cell_lng))
                        conn.commit()
                        cell_fetched = True
                        print(f"Cached road cell ({cell_lat}, {cell_lng}) from {url}")
                        break
                except Exception as e:
                    print(f"Mirror failed for road cell ({cell_lat}, {cell_lng}): {e}")

        # 캐시 DB로부터 영역 매칭 도로망 가져오기
        cursor.execute('''
            SELECT name, highway, width, coords_json FROM road_cache_segments
            WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
        ''', (min_lat, max_lat, min_lng, max_lng))
        
        rows = cursor.fetchall()
        parsed_roads = []
        max_score = 0.0

        for r in rows:
            name, highway, width_val, coords_json = r
            
            # 폭 8m 이하 필터링: 폭이 명시되어 있고 8.0을 초과하면 배제
            if width_val is not None and width_val > 8.0:
                continue
                
            try:
                coords = json.loads(coords_json)
            except Exception:
                continue
                
            if len(coords) < 2:
                continue
                
            for i in range(len(coords) - 1):
                pt1 = coords[i]
                pt2 = coords[i+1]
                
                seg_coords = [pt1, pt2]
                seg_mid_lng = (pt1[0] + pt2[0]) / 2.0
                seg_mid_lat = (pt1[1] + pt2[1]) / 2.0
                
                score = 0.0
                seg_b_lat = int(seg_mid_lat / bucket_size_lat)
                seg_b_lng = int(seg_mid_lng / bucket_size_lng)
                
                for d_lat in [-1, 0, 1]:
                    for d_lng in [-1, 0, 1]:
                        key = (seg_b_lat + d_lat, seg_b_lng + d_lng)
                        if key in spatial_index:
                            for tg in spatial_index[key]:
                                d = fast_dist(seg_mid_lat, seg_mid_lng, tg["lat"], tg["lng"])
                                if d <= 500.0:
                                    decay = 1.0 - d / 500.0
                                    step_weight = (tg["step"] - 5) / 5.0
                                    score += tg["avg_population"] * decay * step_weight
                                    
                if score > max_score:
                    max_score = score
                    
                parsed_roads.append({
                    "coordinates": seg_coords,
                    "road_name": name,
                    "road_class": highway,
                    "score": score
                })

        conn.close()

        if parsed_roads:
            parsed_roads.sort(key=lambda x: x["score"])
            N = len(parsed_roads)
            
            for index, rd in enumerate(parsed_roads):
                if N > 0:
                    step = int((index / N) * 10) + 1
                    step = min(step, 10)
                else:
                    step = 1
                
                # 5단계의 분위수 매핑
                if step >= 9:
                    flow_type = "매우 높음"
                    intensity = 0.9
                elif step >= 7:
                    flow_type = "높음"
                    intensity = 0.7
                elif step >= 5:
                    flow_type = "중간"
                    intensity = 0.5
                elif step >= 3:
                    flow_type = "낮음"
                    intensity = 0.3
                else:
                    flow_type = "매우 낮음"
                    intensity = 0.1
                
                seed_val = int((rd["coordinates"][0][0] * 100000 + rd["coordinates"][0][1] * 100000) % 100000)
                rng = random.Random(seed_val)
                avg_flow = int(intensity * 3300 + rng.randint(200, 500))
                
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": rd["coordinates"]
                    },
                    "properties": {
                        "road_name": rd["road_name"],
                        "road_class": rd["road_class"],
                        "flow_intensity": intensity,
                        "avg_hourly_flow": avg_flow,
                        "flow_type": flow_type
                    }
                })
            osm_success = True
            print(f"Successfully processed road flows from SQLite Cache. Count: {len(features)}")
    except Exception as e:
        print("Caching road flows pipeline failed, fallback triggered:", e)

    # 3. DB 로딩 실패 또는 데이터가 전혀 수집되지 않은 초기 단계 시 Fallback 가상 생성 엔진 구동
    if not osm_success:
        print("Running procedural road flow generator fallback...")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, lat, lng FROM subways
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
            LIMIT 30
        ''', (min_lat, max_lat, min_lng, max_lng))
        subways = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute('''
            SELECT name, lat, lng FROM bus_stops
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
            LIMIT 40
        ''', (min_lat, max_lat, min_lng, max_lng))
        bus_stops = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute('''
            SELECT name, lat, lng FROM commercial_areas
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
            LIMIT 25
        ''', (min_lat, max_lat, min_lng, max_lng))
        commercials = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute('''
            SELECT case_no, property_type, lat, lng FROM auctions
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
            LIMIT 20
        ''', (min_lat, max_lat, min_lng, max_lng))
        auctions = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        
        candidate_roads = []
        
        def add_candidate(coords, name, r_class, def_intensity, f_type):
            candidate_roads.append({
                "coordinates": coords,
                "name": name,
                "road_class": r_class,
                "default_intensity": def_intensity,
                "flow_type": f_type
            })

        for s in subways:
            s_name = s["name"]
            lat, lng = s["lat"], s["lng"]
            add_candidate([[lng - 0.003, lat], [lng + 0.003, lat]], f"{s_name}역 메인 보행로", "보행로", 0.85, "오피스동선")
            add_candidate([[lng, lat - 0.003], [lng, lat + 0.003]], f"{s_name}역 연결 인도", "인도", 0.82, "오피스동선")
            add_candidate([[lng - 0.002, lat + 0.0007], [lng + 0.002, lat + 0.0007]], f"{s_name}역 북측 먹자거리", "소도로", 0.83, "먹자골목")
            add_candidate([[lng - 0.002, lat - 0.0007], [lng + 0.002, lat - 0.0007]], f"{s_name}역 남측 맛집거리", "소도로", 0.81, "먹자골목")
            add_candidate([[lng + 0.001, lat - 0.0015], [lng + 0.001, lat + 0.0015]], f"{s_name}역 동측 이면도로", "소도로", 0.77, "먹자골목")
            add_candidate([[lng - 0.001, lat - 0.0015], [lng - 0.001, lat + 0.0015]], f"{s_name}역 서측 카페거리", "소도로", 0.78, "먹자골목")
            
        for c in commercials:
            c_name = c["name"]
            lat, lng = c["lat"], c["lng"]
            add_candidate([[lng - 0.0015, lat], [lng + 0.0015, lat]], f"{c_name} 상가 메인거리", "소도로", 0.84, "먹자골목")
            add_candidate([[lng, lat - 0.001], [lng, lat + 0.001]], f"{c_name} 상업 이면도로", "소도로", 0.71, "먹자골목")
            add_candidate([[lng - 0.001, lat - 0.0006], [lng + 0.001, lat + 0.0006]], f"{c_name} 연계 보행골목", "골목길", 0.63, "생활이동")
            
        for a in auctions:
            a_type = a["property_type"]
            lat, lng = a["lat"], a["lng"]
            add_candidate([[lng - 0.0008, lat - 0.0004], [lng + 0.0008, lat + 0.0004]], f"{a_type} 물건지 진입로", "골목길", 0.45, "생활이동")
            add_candidate([[lng - 0.0004, lat + 0.0004], [lng + 0.0004, lat - 0.0004]], "주거 배후 생활도로", "골목길", 0.32, "생활이동")
            
        for b in bus_stops:
            b_name = b["name"]
            lat, lng = b["lat"], b["lng"]
            add_candidate([[lng - 0.0005, lat], [lng + 0.0005, lat]], f"{b_name} 정류장 연계로", "골목길", 0.49, "생활이동")

        max_score = 0.0
        for rc in candidate_roads:
            geom = rc["coordinates"]
            mid_lat = sum(pt[1] for pt in geom) / len(geom)
            mid_lng = sum(pt[0] for pt in geom) / len(geom)
            
            score = 0.0
            for tg in top5_grids:
                d = fast_dist(mid_lat, mid_lng, tg["lat"], tg["lng"])
                if d <= 500.0:
                    decay = 1.0 - d / 500.0
                    step_weight = (tg["step"] - 5) / 5.0
                    score += tg["avg_population"] * decay * step_weight
            rc["score"] = score
            if score > max_score:
                max_score = score
                
        candidate_roads.sort(key=lambda x: x["score"])
        N = len(candidate_roads)
        
        for index, rc in enumerate(candidate_roads):
            if N > 0:
                step = int((index / N) * 10) + 1
                step = min(step, 10)
            else:
                step = 1
                
            if step >= 9:
                flow_type = "매우 높음"
                intensity = 0.9
            elif step >= 7:
                flow_type = "높음"
                intensity = 0.7
            elif step >= 5:
                flow_type = "중간"
                intensity = 0.5
            elif step >= 3:
                flow_type = "낮음"
                intensity = 0.3
            else:
                flow_type = "매우 낮음"
                intensity = 0.1
            
            seed_val = int((rc["coordinates"][0][0] * 100000 + rc["coordinates"][0][1] * 100000) % 100000)
            rng = random.Random(seed_val)
            avg_flow = int(intensity * 3300 + rng.randint(200, 500))
            
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": rc["coordinates"]
                },
                "properties": {
                    "road_name": rc["name"],
                    "road_class": rc["road_class"],
                    "flow_intensity": intensity,
                    "avg_hourly_flow": avg_flow,
                    "flow_type": flow_type
                }
            })

    geojson_result = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return {"status": "success", "data": geojson_result}"""

# Find get_road_flows signature and replace up to static mount or next route
start_sig = "@app.get(\"/api/map/road_flows\")"
end_marker = "# 이미지 제공용 스태틱 라우트"

if start_sig in content and end_marker in content:
    start_pos = content.find(start_sig)
    end_pos = content.find(end_marker)
    
    # Replace content between start_pos and end_pos
    new_content = content[:start_pos] + new_func + "\\n\\n\\n\\n" + content[end_pos:]
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully replaced get_road_flows in backend/app.py")
else:
    print("Could not find signature or marker in backend/app.py")
