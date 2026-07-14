import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://openapi.gg.go.kr/TBGRISCTYRVBSNSM"
api_key = "babef8969e9c4d1884b50ea5e4fbee88"
headers = {"User-Agent": "Mozilla/5.0"}

params = {
    "KEY": api_key,
    "Type": "json",
    "pIndex": 1,
    "pSize": 1
}

res = requests.get(url, params=params, headers=headers, verify=False)
data = res.json()
row = data["TBGRISCTYRVBSNSM"][1]["row"][0]
print("Row Keys:", list(row.keys()))
print("Row Data:")
for k, v in row.items():
    print(f"  {k}: {repr(v)}")
