# -*- coding: utf-8 -*-
import geopandas as gpd
import sqlite3
import json
import requests
from shapely.geometry import Point, mapping
import os

db_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"
shp_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\gris_shp\Gyeonggi_Jeongbi_Guyeok.shp"
openapi_url = "https://openapi.gg.go.kr/TBGRISCTYRVBSNSM"
api_key = "babef8969e9c4d1884b50ea5e4fbee88"

def get_sgg_name(sgg_cd):
    if not sgg_cd:
        return ""
    exact_code = str(sgg_cd)[:5]
    exact_mapping = {
        '41110': '수원시', '41111': '수원시 장안구', '41113': '수원시 권선구', '41115': '수원시 팔달구', '41117': '수원시 영통구',
        '41130': '성남시', '41131': '성남시 수정구', '41133': '성남시 중원구', '41135': '성남시 분당구',
        '41150': '의정부시',
        '41170': '안양시', '41171': '안양시 만안구', '41173': '안양시 동안구',
        '41190': '부천시', '41210': '광명시',
        '41220': '평택시', '41250': '동두천시',
        '41270': '안산시', '41271': '안산시 상록구', '41273': '안산시 단원구',
        '41280': '고양시', '41281': '고양시 덕양구', '41285': '고양시 일산동구', '41287': '고양시 일산서구',
        '41290': '과천시', '41310': '구리시', '41360': '남양주시', '41370': '오산시', '41390': '시흥시', '41410': '군포시',
        '41430': '의왕시', '41450': '하남시',
        '41460': '용인시', '41461': '용인시 처인구', '41463': '용인시 기흥구', '41465': '용인시 수지구',
        '41480': '파주시', '41500': '이천시', '41550': '안성시', '41570': '김포시', '41590': '화성시',
        '41610': '광주시', '41630': '양주시', '41650': '포천시', '41670': '여주시',
        '41800': '연천군', '41820': '가평군', '41830': '양평군'
    }
    if exact_code in exact_mapping:
        return exact_mapping[exact_code]
        
    code_4 = str(sgg_cd)[:4]
    prefix_mapping = {
        '4111': '수원시', '4113': '성남시', '4117': '안양시', '4127': '안산시', '4128': '고양시', '4146': '용인시'
    }
    if code_4 in prefix_mapping:
        return prefix_mapping[code_4]
        
    return ""

def map_propel_code(stage):
    s = str(stage).strip()
    if '준공' in s:
        return 'PP0706'
    elif '착공' in s:
        return 'PP0602'
    elif '관리처분' in s:
        return 'PP0601'
    elif '사업시행' in s:
        return 'PP0402'
    elif '조합설립' in s:
        return 'PP0204'
    elif '정비구역지정' in s or '구역지정' in s:
        return 'PP0103'
    elif '추진위' in s:
        return 'PP0102'
    elif '후보지' in s:
        return 'PP0101'
    else:
        return 'PP0101'

def main():
    if not os.path.exists(db_path):
        print("DB not found!")
        return
    if not os.path.exists(shp_path):
        print("Shapefile not found!")
        return

    # 1. Fetch OpenAPI Gyeonggi redevelopment data in real-time
    print("Fetching Gyeonggi redevelopment data from OpenAPI...")
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {
        "KEY": api_key,
        "Type": "json",
        "pIndex": 1,
        "pSize": 1000
    }
    
    api_rows = []
    try:
        res = requests.get(openapi_url, params=params, headers=headers, verify=False, timeout=15)
        if res.status_code == 200:
            res.encoding = 'utf-8'
            res_json = res.json()
            if "TBGRISCTYRVBSNSM" in res_json:
                api_rows = res_json["TBGRISCTYRVBSNSM"][1]["row"]
                print(f"Loaded {len(api_rows)} rows from Gyeonggi OpenAPI.")
            else:
                print("OpenAPI response had unexpected format.")
        else:
            print(f"OpenAPI request failed with code {res.status_code}.")
    except Exception as e:
        print(f"Error fetching Gyeonggi OpenAPI data: {e}")

    # 2. Load Shapefile
    print("Loading Shapefile...")
    gdf = gpd.read_file(shp_path, encoding='cp949')
    print(f"Loaded {len(gdf)} Shapefile polygons.")

    # 3. Connect to SQLite DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 4. Clear existing Gyeonggi entries in database
    print("\nClearing old Gyeonggi entries from DB...")
    cursor.execute("DELETE FROM redevelopment_zones WHERE name LIKE '[경기]%'")
    conn.commit()

    # 5. Migrate all 363 Shapefile records
    print(f"Migrating {len(gdf)} Shapefile polygons into redevelopment_zones...")
    success_count = 0

    for idx, shp_row in gdf.iterrows():
        geom = shp_row['geometry']
        if not geom:
            continue
            
        bounds = geom.bounds # (minx, miny, maxx, maxy)
        min_lng, min_lat, max_lng, max_lat = bounds
        
        geojson_str = json.dumps(mapping(geom))
        
        # Get shapefile attributes
        shp_id = shp_row['id']
        shp_name = str(shp_row['name']).strip() if shp_row['name'] else ""
        shp_remark = str(shp_row['remark']).strip() if shp_row['remark'] else ""
        sgg_cd = shp_row.get('sgg_cd', '')
        use_cd = shp_row.get('use_cd', 'UDT100')
        area_val = shp_row.get('shape.area', 10000.0)
        
        # Try to match with an OpenAPI row by name
        matched_api_row = None
        if shp_name and shp_name != "None" and shp_name != "정비구역" and shp_name != "정비예정구역":
            # Search by name in api_rows
            for ar in api_rows:
                ar_zone_name = str(ar.get('imprv_zone_nm', '')).strip()
                if ar_zone_name and (shp_name in ar_zone_name or ar_zone_name in shp_name):
                    matched_api_row = ar
                    break
        
        if not matched_api_row and shp_remark and shp_remark != "None" and "행위제한" not in shp_remark and "예정구역" not in shp_remark:
            # Search by remark in api_rows
            for ar in api_rows:
                ar_zone_name = str(ar.get('imprv_zone_nm', '')).strip()
                if ar_zone_name and (shp_remark in ar_zone_name or ar_zone_name in shp_remark):
                    matched_api_row = ar
                    break

        if matched_api_row:
            # Match found! Use official OpenAPI name, stage, and business type
            sigun_nm = matched_api_row.get('sigun_nm', '')
            zone_name = matched_api_row.get('imprv_zone_nm', '')
            biz_step = matched_api_row.get('biz_step', '')
            biz_type = matched_api_row.get('biz_type', '재개발')
            
            # Use actual shapefile area if shape.area exists
            try:
                area_m2 = int(float(area_val))
            except ValueError:
                area_m2 = 10000
                
            propel_cd = map_propel_code(biz_step)
            
            prefix = f"[경기] {sigun_nm} " if sigun_nm else "[경기] "
            display_name = f"{prefix}{zone_name} ({biz_type}, {biz_step}, {area_m2:,}㎡)"
            
        else:
            # Guess properties for unmatched GIS layer
            sgg_name = get_sgg_name(sgg_cd)
            
            # Construct zone_name
            zone_name = ""
            if shp_name and shp_name != "None" and shp_name != "정비구역" and shp_name != "정비예정구역":
                zone_name = shp_name
            elif shp_remark and shp_remark != "None" and "행위제한" not in shp_remark:
                zone_name = shp_remark
            else:
                zone_name = f"정비구역 {shp_id}"
                
            # Guess biz_type
            biz_type = "재개발"
            if "재건축" in shp_name or "재건축" in shp_remark:
                biz_type = "재건축"
            elif "재개발" in shp_name or "재개발" in shp_remark:
                biz_type = "재개발"
            elif "도시개발" in shp_name or "도시개발" in shp_remark:
                biz_type = "도시개발"
                
            # Guess propel_cd
            stage_text = "정비구역지정"
            propel_cd = "PP0103" # Default: Designated 정비구역
            
            if use_cd == "UDT999" or "예정구역" in shp_name or "예정구역" in shp_remark or "후보지" in shp_name or "후보지" in shp_remark or "행위제한" in shp_name or "행위제한" in shp_remark:
                propel_cd = "PP0101" # 예정구역 / 후보지
                stage_text = "예정구역"
                
            try:
                area_m2 = int(float(area_val))
            except ValueError:
                area_m2 = 10000
                
            prefix = f"[경기] {sgg_name} " if sgg_name else "[경기] "
            display_name = f"{prefix}{zone_name} ({biz_type}, {stage_text}, {area_m2:,}㎡)"
            
        cursor.execute('''
            INSERT INTO redevelopment_zones (name, propel_cd, min_lat, max_lat, min_lng, max_lng, geojson)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (display_name, propel_cd, min_lat, max_lat, min_lng, max_lng, geojson_str))
        success_count += 1

    conn.commit()
    conn.close()
    
    print(f"\n=========================================")
    print(f"Migration Finished!")
    print(f"Successfully migrated {success_count} Gyeonggi detailed polygons to Database.")
    print(f"=========================================")

if __name__ == '__main__':
    main()
