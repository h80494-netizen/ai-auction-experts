import os
import time
import requests
import pandas as pd
import json

KAKAO_AK = "KakaoAK 9e5265220f87e54e4379077cb60071bb"
HEADERS = {"Authorization": KAKAO_AK}

excel_path = 'c:/Users/llll/Documents/두인경매/바이브코딩/data/아파트단지정보.xlsx'
out_dir = 'c:/Users/llll/Documents/두인경매/바이브코딩/public/data'
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'apt_info.geojson')

print(f"Loading {excel_path}...")
df = pd.read_excel(excel_path)

features = []

print(f"Processing {len(df)} rows...")
for idx, row in df.iterrows():
    # Address logic
    addr = str(row.get('도로명주소', ''))
    if pd.isna(addr) or addr.strip() == '':
        addr = str(row.get('법정동주소', ''))
    
    if pd.isna(addr) or addr.strip() == '' or addr.strip() == 'nan':
        continue
    
    # Clean address
    query = addr.split(',')[0].split('(')[0].strip()
    
    # Geocode
    url = f"https://dapi.kakao.com/v2/local/search/address.json?query={query}"
    try:
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        if data.get('documents'):
            doc = data['documents'][0]
            lng = float(doc['x'])
            lat = float(doc['y'])
        else:
            # Try keyword search as fallback
            k_url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={query}"
            k_res = requests.get(k_url, headers=HEADERS)
            k_data = k_res.json()
            if k_data.get('documents'):
                doc = k_data['documents'][0]
                lng = float(doc['x'])
                lat = float(doc['y'])
            else:
                print(f"Geocoding failed for {query}")
                continue
    except Exception as e:
        print(f"API Error for {query}: {e}")
        continue
        
    # Calculate properties
    try:
        households = float(row.get('세대수', 0))
    except:
        households = 0
        
    try:
        parking = float(row.get('총주차대수', 0))
    except:
        parking = 0
        
    parking_ratio = round(parking / households, 2) if households > 0 else 0
    
    approval_date = str(row.get('사용승인일', ''))
    build_year = approval_date[:4] if len(approval_date) >= 4 else 'N/A'
    
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [lng, lat]
        },
        "properties": {
            "name": str(row.get('단지명', '알 수 없음')),
            "address": addr,
            "households": int(households),
            "parking_total": int(parking),
            "parking_ratio": parking_ratio,
            "build_year": build_year
        }
    }
    features.append(feature)
    
    # Rate limit prevention
    time.sleep(0.05)
    
    if (idx + 1) % 100 == 0:
        print(f"Processed {idx + 1}/{len(df)}")

geojson_data = {
    "type": "FeatureCollection",
    "features": features
}

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(geojson_data, f, ensure_ascii=False)

print(f"Saved {len(features)} apartment locations to {out_path}.")
