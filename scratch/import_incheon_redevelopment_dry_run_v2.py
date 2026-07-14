import pandas as pd
import requests
import time
import os

csv_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\data\인천재개발추진현황_20260430.csv"

if not os.path.exists(csv_path):
    print("CSV not found!")
    exit(1)

df = pd.read_csv(csv_path, encoding='cp949')

def clean_address(district, raw_addr):
    addr = str(raw_addr)
    for delimiter in ['및', '일원', '일대', '외', '(']:
        addr = addr.split(delimiter)[0].strip()
    addr = addr.replace('번지', '').strip()
    addr = ' '.join(addr.split())
    return f"인천 {district} {addr}"

print("Dry run geocoding v2 for first 8 rows:")
for idx, row in df.head(8).iterrows():
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
        "User-Agent": "AntigravityAI-IncheonRedevImporterV2/1.0"
    }
    
    try:
        res = requests.get(url, params=params, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data:
                lat = float(data[0]['lat'])
                lng = float(data[0]['lon'])
                # Convert printable string representation to prevent CP949 logging errors
                print(f"Row {idx} [{repr(zone_name)}]: address={repr(cleaned_addr)} -> lat={lat}, lng={lng}")
            else:
                # Try a broader address search if specific number failed, e.g. "인천 중구 사동" instead of "인천 중구 사동 23-4"
                # split by space and take up to the last word
                parts = cleaned_addr.split()
                if len(parts) > 3:
                    broad_addr = ' '.join(parts[:-1])
                    res_broad = requests.get(url, params={"q": broad_addr, "format": "json", "limit": 1}, headers=headers, timeout=5)
                    data_broad = res_broad.json() if res_broad.status_code == 200 else []
                    if data_broad:
                        lat = float(data_broad[0]['lat'])
                        lng = float(data_broad[0]['lon'])
                        print(f"Row {idx} [{repr(zone_name)}]: address={repr(cleaned_addr)} (BROAD match: {repr(broad_addr)}) -> lat={lat}, lng={lng}")
                        continue
                print(f"Row {idx} [{repr(zone_name)}]: address={repr(cleaned_addr)} -> NOT found.")
        else:
            print(f"Row {idx} [{repr(zone_name)}]: Failed with status {res.status_code}")
    except Exception as e:
        print(f"Row {idx} [{repr(zone_name)}]: Error: {e}")
        
    time.sleep(1)
