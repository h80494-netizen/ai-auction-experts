import os
import pandas as pd
import json

excel_path = 'c:/Users/llll/Documents/두인경매/바이브코딩/data/아파트단지정보.xlsx'
out_path = 'c:/Users/llll/Documents/두인경매/바이브코딩/public/data/apt_info.geojson'

print(f"Loading {excel_path}...")
df = pd.read_excel(excel_path)

# Print columns to see the exact names of the new ones
cols = df.columns.tolist()
print("Total columns:", len(cols))
print("Last 5 columns:", cols[-5:])

features = []
count = 0

# Assume the new columns are named '경도', '위도' or we can access by index 85, 86 (CH, CI)
for idx, row in df.iterrows():
    # Use pandas iloc to reliably get the 86th (CH) and 87th (CI) columns
    # CH is index 85, CI is index 86
    try:
        lng_val = row.iloc[85]
        lat_val = row.iloc[86]
    except IndexError:
        print(f"Row {idx} missing CH/CI columns")
        continue

    # Clean the coordinate values (sometimes there are NaNs)
    if pd.isna(lng_val) or pd.isna(lat_val):
        continue
    
    try:
        lng = float(lng_val)
        lat = float(lat_val)
    except:
        continue

    # Properties
    addr = str(row.get('도로명주소', ''))
    if pd.isna(addr) or addr.strip() == '':
        addr = str(row.get('법정동주소', ''))
    
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
    count += 1

geojson_data = {
    "type": "FeatureCollection",
    "features": features
}

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(geojson_data, f, ensure_ascii=False)

print(f"Saved {count} apartment locations to {out_path}.")
