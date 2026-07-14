import requests
import json

url = "https://openapi.gg.go.kr/GnrlMaintBizPromtStat"
params = {
    "KEY": "babef8969e9c4d1884b50ea5e4fbee8",
    "Type": "json",
    "pIndex": 1,
    "pSize": 5
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

try:
    response = requests.get(url, params=params, headers=headers, verify=False)
    print("Status Code:", response.status_code)
    print("Response Length:", len(response.text))
    # Print first 2000 characters
    print(response.text[:2000])
    
    # Save to a file to inspect full response if it succeeded
    if response.status_code == 200:
        with open("scratch/gg_api_sample.json", "w", encoding="utf-8") as f:
            f.write(response.text)
except Exception as e:
    print("Request failed:", e)
