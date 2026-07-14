import requests

headers = {"User-Agent": "AntigravityAI-Test/1.0"}

for addr in ["인천 중구 경동 40번지", "인천 중구 경동 40"]:
    res = requests.get("https://nominatim.openstreetmap.org/search", params={"q": addr, "format": "json", "limit": 1}, headers=headers)
    print(f"Address: {addr} | Status: {res.status_code} | Found: {len(res.json()) > 0}")
