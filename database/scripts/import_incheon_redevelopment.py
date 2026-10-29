# -*- coding: utf-8 -*-
import pandas as pd
import requests
import sqlite3
import json
import math
import os
import time

csv_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\data\인천재개발추진현황_20260430.csv"
db_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\data\map_data.db"

if not os.path.exists(csv_path):
    print("CSV not found!")
    exit(1)

if not os.path.exists(db_path):
    print("Database not found!")
    exit(1)

df = pd.read_csv(csv_path, encoding='cp949')

def clean_address(district, raw_addr):
    addr = str(raw_addr)
    for delimiter in ['및', '일원', '일대', '외', '(']:
        addr = addr.split(delimiter)[0].strip()
    addr = addr.replace('번지', '').strip()
    addr = ' '.join(addr.split())
    return f"인천광역시 {district} {addr}"

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
    elif '정비구역지정' in s:
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

# Remove existing Incheon entries to make it idempotent
cursor.execute("DELETE FROM redevelopment_zones WHERE name LIKE '[인천]%'")
conn.commit()

print(f"Cleared existing Incheon entries. Importing {len(df)} rows...")

success_count = 0
fail_count = 0

headers = {
    "User-Agent": "AntigravityAI-IncheonRedevImporter/1.0"
}

for idx, row in df.iterrows():
    district = row['구명']
    zone_name = row['구 역 명']
    raw_addr = row['위치']
    area = float(row['면적(제곱미터)     ']) if not pd.isna(row['면적(제곱미터)     ']) else 10000.0
    stage = row['진행단계']
    
    cleaned_addr = clean_address(district, raw_addr)
    propel_cd = map_propel_code(stage)
    
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": cleaned_addr,
        "format": "json",
        "limit": 1
    }
    
    lat, lng = None, None
    try:
        res = requests.get(url, params=params, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data:
                lat = float(data[0]['lat'])
                lng = float(data[0]['lon'])
            else:
                # Fallback to broad address match
                parts = cleaned_addr.split()
                if len(parts) > 3:
                    broad_addr = ' '.join(parts[:-1])
                    res_broad = requests.get(url, params={"q": broad_addr, "format": "json", "limit": 1}, headers=headers, timeout=5)
                    data_broad = res_broad.json() if res_broad.status_code == 200 else []
                    if data_broad:
                        lat = float(data_broad[0]['lat'])
                        lng = float(data_broad[0]['lon'])
    except Exception as e:
        print(f"Error querying Nominatim for row {idx}: {e}")
        
    if lat is not None and lng is not None:
        # Generate a circular polygon representing the redevelopment area
        # 1 degree lat = 111000 meters. 1 degree lng = 88000 meters at Incheon latitude.
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
        display_name = f"[인천] {zone_name} ({row['사업유형']}, {stage}, {int(area):,}㎡)"
        
        cursor.execute('''
            INSERT INTO redevelopment_zones (name, propel_cd, min_lat, max_lat, min_lng, max_lng, geojson)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (display_name, propel_cd, min_lat, max_lat, min_lng, max_lng, geojson_str))
        
        success_count += 1
        print(f"[{success_count}/{len(df)}] Imported: {zone_name} -> lat={lat:.5f}, lng={lng:.5f}")
    else:
        fail_count += 1
        print(f"[FAIL] Could not geocode address: {cleaned_addr} for zone: {zone_name}")
        
    conn.commit()
    # 1 second delay as required by Nominatim usage policy
    time.sleep(1)

conn.close()
print(f"\n=========================================")
print(f"Import Finished!")
print(f"Successfully geocoded and imported: {success_count} zones.")
print(f"Failed to geocode: {fail_count} zones.")
print(f"=========================================")
