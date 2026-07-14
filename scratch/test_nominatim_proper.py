import requests
import json

address = "인천 중구 경동 40"
url = "https://nominatim.openstreetmap.org/search"
params = {
    "q": address,
    "format": "json",
    "limit": 1
}
headers = {
    "User-Agent": "AntigravityAI-IncheonTest/1.0"
}

try:
    res = requests.get(url, params=params, headers=headers, timeout=5)
    print("Status:", res.status_code)
    data = res.json()
    if data:
        print("Success!")
        print("lat:", data[0]['lat'])
        print("lon:", data[0]['lon'])
    else:
        print("No results found.")
except Exception as e:
    print("Error:", e)
