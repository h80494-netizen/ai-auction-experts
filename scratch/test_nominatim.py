import requests
import time

address = "인천 중구 경동 40"
url = "https://nominatim.openstreetmap.org/search"
params = {
    "q": address,
    "format": "json",
    "limit": 1
}

headers = {
    "User-Agent": "AntigravityAI-AppDeveloper-Client/1.0 (contact@google.com)"
}

try:
    print(f"Querying Nominatim for: {address} ...")
    res = requests.get(url, params=params, headers=headers, timeout=5)
    print("Status:", res.status_code)
    print("Response:")
    print(res.text)
except Exception as e:
    print("Failed:", e)
