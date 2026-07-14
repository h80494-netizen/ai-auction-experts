import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://openapi.gg.go.kr/TBGRISCTYRVBSNSM"
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
    print(f"Querying Gyeonggi API: {url} ...")
    res = requests.get(url, params=params, headers=headers, verify=False, timeout=10)
    print("Status:", res.status_code)
    print("Response Length:", len(res.text))
    # Print sample
    print(res.text[:1000])
except Exception as e:
    print("Error:", e)
