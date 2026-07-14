import requests
import json

url = "https://openapi.gg.go.kr/TBGRISCTYRVBSNSM"
api_key = "babef8969e9c4d1884b50ea5e4fbee88"
params = {
    "KEY": api_key,
    "Type": "json",
    "pIndex": 1,
    "pSize": 5
}
headers = {
    "User-Agent": "Mozilla/5.0"
}

res = requests.get(url, params=params, headers=headers, verify=False, timeout=10)
data = res.json()
print("Raw API response:")
rows = data["TBGRISCTYRVBSNSM"][1]["row"]
for r in rows:
    print(r.get('sigun_nm'), r.get('imprv_zone_nm'), r.get('loc'))
