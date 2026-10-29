# -*- coding: utf-8 -*-
import requests
import sqlite3
import json
import math
import os
import time

url = "https://openapi.gg.go.kr/TBGRISCTYRVBSNSM"
db_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"
api_key = "babef8969e9c4d1884b50ea5e4fbee88"

if not os.path.exists(db_path):
    print("Database not found!")
    exit(1)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

params = {
    "KEY": api_key,
    "Type": "json",
    "pIndex": 1,
    "pSize": 1000  # Fetch all 493 rows in a single batch
}

try:
    print("Fetching Gyeonggi redevelopment data from OpenAPI...")
    res = requests.get(url, params=params, headers=headers, verify=False, timeout=15)
    if res.status_code != 200:
        print(f"API request failed with status: {res.status_code}")
        exit(1)
        
    res.encoding = 'utf-8' # Explicitly force UTF-8 encoding
    data = res.json()
    if "TBGRISCTYRVBSNSM" not in data:
        print("Invalid API response structure:", list(data.keys()))
        exit(1)
        
    rows = data["TBGRISCTYRVBSNSM"][1]["row"]
    print(f"Successfully fetched {len(rows)} Gyeonggi redevelopment zones!")
    
except Exception as e:
    print("Failed to query Gyeonggi API:", e)
    exit(1)

def clean_address(raw_addr):
    addr = str(raw_addr)
    for delimiter in ['및', '일원', '일대', '외', '(']:
        addr = addr.split(delimiter)[0].strip()
    addr = addr.replace('번지', '').strip()
    addr = ' '.join(addr.split())
    return addr

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

# Connect to DB
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Remove existing Gyeonggi entries to make it idempotent
cursor.execute("DELETE FROM redevelopment_zones WHERE name LIKE '[경기]%'")
conn.commit()

print(f"Cleared existing Gyeonggi entries in DB. Importing {len(rows)} rows...")

success_count = 0
fail_count = 0

for idx, r in enumerate(rows):
    sigun = r.get('sigun_nm', '')
    zone_name = r.get('imprv_zone_nm', '')
    raw_addr = r.get('loc', '')
    area = r.get('zone_ar')
    stage = r.get('biz_step', '')
    biz_type = r.get('biz_type', '재개발')
    
    # Check area validity
    try:
        area = float(area) if area is not None else 10000.0
    except ValueError:
        area = 10000.0
        
    cleaned_addr = clean_address(raw_addr)
    # Prepend province and city prefix for maximum geocoding precision
    query_addr = cleaned_addr
    if sigun and not cleaned_addr.startswith("경기"):
        query_addr = f"경기도 {sigun} {cleaned_addr}"
        
    propel_cd = map_propel_code(stage)
    
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params_geo = {
        "q": query_addr,
        "format": "json",
        "limit": 1
    }
    
    lat, lng = None, None
    try:
        res_geo = requests.get(nominatim_url, params=params_geo, headers=headers, timeout=5)
        if res_geo.status_code == 200:
            data_geo = res_geo.json()
            if data_geo:
                lat = float(data_geo[0]['lat'])
                lng = float(data_geo[0]['lon'])
            else:
                # Fallback to broader address match (e.g. drop house number)
                parts = query_addr.split()
                if len(parts) > 3:
                    broad_addr = ' '.join(parts[:-1])
                    res_broad = requests.get(nominatim_url, params={"q": broad_addr, "format": "json", "limit": 1}, headers=headers, timeout=5)
                    data_broad = res_broad.json() if res_broad.status_code == 200 else []
                    if data_broad:
                        lat = float(data_broad[0]['lat'])
                        lng = float(data_broad[0]['lon'])
    except Exception as e:
        print(f"Error querying Nominatim for row {idx}: {e}")
        
    if lat is not None and lng is not None:
        # Generate a circular polygon representing the redevelopment area
        # 1 degree lat = 111000 meters. 1 degree lng = 88000 meters at Gyeonggi latitude.
        radius = math.sqrt(area / math.pi)
        r_lat = radius / 111000.0
        r_lng = radius / 88000.0
        
        num_points = 16
        coords = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = lng + r_lng * math.cos(angle)
            y = lat + r_lat * math.sin(angle)
            coords.append([x, y])
        coords.append(coords[0])  # Close the polygon
        
        geojson_dict = {
            "type": "Polygon",
            "coordinates": [coords]
        }
        geojson_str = json.dumps(geojson_dict)
        
        min_lat = lat - r_lat
        max_lat = lat + r_lat
        min_lng = lng - r_lng
        max_lng = lng + r_lng
        
        # Display name in popup
        display_name = f"[경기] {zone_name} ({biz_type}, {stage}, {int(area):,}㎡)"
        
        cursor.execute('''
            INSERT INTO redevelopment_zones (name, propel_cd, min_lat, max_lat, min_lng, max_lng, geojson)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (display_name, propel_cd, min_lat, max_lat, min_lng, max_lng, geojson_str))
        
        success_count += 1
        print(f"[{success_count}/{len(rows)}] Imported Gyeonggi: {zone_name} -> lat={lat:.5f}, lng={lng:.5f}")
    else:
        fail_count += 1
        print(f"[FAIL] Could not geocode address: {cleaned_addr} for zone: {zone_name}")
        
    conn.commit()
    # 1 second delay as required by Nominatim usage policy
    time.sleep(1)

conn.close()
print(f"\n=========================================")
print(f"Gyeonggi Import Finished!")
print(f"Successfully geocoded and imported: {success_count} Gyeonggi zones.")
print(f"Failed to geocode: {fail_count} Gyeonggi zones.")
print(f"=========================================")
