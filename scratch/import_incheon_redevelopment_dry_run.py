import pandas as pd
import requests
import json
import math
import os
import time

csv_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\data\인천재개발추진현황_20260430.csv"

if not os.path.exists(csv_path):
    print("CSV not found!")
    exit(1)

df = pd.read_csv(csv_path, encoding='cp949')

def clean_address(district, raw_addr):
    # 경동 40번지 및 율목동 10번지 일원 -> 경동 40번지
    addr = str(raw_addr)
    # Split by common delimiters to get the first main address
    for delimiter in ['및', '일원', '일대', '외', '(']:
        addr = addr.split(delimiter)[0].strip()
    return f"인천 {district} {addr}"

# Test geocoding for first 5 rows
print("Dry run geocoding for first 5 rows:")
for idx, row in df.head(5).iterrows():
    district = row['구명']
    zone_name = row['구 역 명']
    raw_addr = row['위치']
    cleaned_addr = clean_address(district, raw_addr)
    
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": cleaned_addr,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "AntigravityAI-IncheonRedevImporter/1.0 (contact@google.com)"
    }
    
    try:
        print(f"\nRow {idx}: {zone_name} | Cleaned address: {cleaned_addr}")
        res = requests.get(url, params=params, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data:
                lat = float(data[0]['lat'])
                lng = float(data[0]['lon'])
                print(f" -> Found: lat={lat}, lng={lng}")
            else:
                print(" -> No coordinates found.")
        else:
            print(f" -> Failed with status code: {res.status_code}")
    except Exception as e:
        print(" -> Error geocoding:", e)
    
    # 1 second delay as required by Nominatim usage policy
    time.sleep(1)
