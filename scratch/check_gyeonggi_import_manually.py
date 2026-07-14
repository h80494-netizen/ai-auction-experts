import requests
import json
import math
import os
import time

url = "https://openapi.gg.go.kr/TBGRISCTYRVBSNSM"
api_key = "babef8969e9c4d1884b50ea5e4fbee88"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

params = {
    "KEY": api_key,
    "Type": "json",
    "pIndex": 1,
    "pSize": 3  # Try 3 rows
}

try:
    print("Testing Gyeonggi API...")
    res = requests.get(url, params=params, headers=headers, verify=False, timeout=10)
    print("Status:", res.status_code)
    print("Response Length:", len(res.text))
    data = res.json()
    if "TBGRISCTYRVBSNSM" in data:
        rows = data["TBGRISCTYRVBSNSM"][1]["row"]
        print("Success! Sample Gyeonggi rows:")
        for r in rows:
            print(f"Name: {r.get('IMPRV_ZONE_NM')} | Loc: {r.get('LOC')} | Stage: {r.get('BIZ_STEP')}")
    else:
        print("Invalid response keys:", data.keys())
except Exception as e:
    print("Error:", e)
