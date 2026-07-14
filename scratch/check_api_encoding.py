import requests

url = "https://openapi.gg.go.kr/TBGRISCTYRVBSNSM"
api_key = "babef8969e9c4d1884b50ea5e4fbee88"
params = {
    "KEY": api_key,
    "Type": "json",
    "pIndex": 1,
    "pSize": 2
}
headers = {
    "User-Agent": "Mozilla/5.0"
}

try:
    res = requests.get(url, params=params, headers=headers, verify=False, timeout=30)
    print("Status:", res.status_code)
    print("Content-Type header:", res.headers.get("Content-Type"))
    print("Encoding:", res.encoding)
    print("Apparent Encoding:", res.apparent_encoding)
    
    # Write raw bytes to file
    with open("scratch/raw_api_res.txt", "wb") as f:
        f.write(res.content)
        
    print("Wrote raw content to scratch/raw_api_res.txt")
except Exception as e:
    print("Error:", e)
