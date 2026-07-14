import requests

try:
    url = "http://localhost:8000/api/map/redevelopment_zones?min_lat=37.4&max_lat=37.6&min_lng=126.9&max_lng=127.1"
    r = requests.get(url)
    print("Status code:", r.status_code)
    print("Headers:", r.headers)
    print("Response snippet:", r.text[:500])
except Exception as e:
    print("Connection error:", e)
