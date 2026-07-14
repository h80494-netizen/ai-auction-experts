import requests
import time

endpoints = [
    "/api/map/subway_lines",
    "/api/map/auctions?min_lat=37.51&max_lat=37.52&min_lng=127.07&max_lng=127.08",
]

for ep in endpoints:
    url = f"http://127.0.0.1:8000{ep}"
    print(f"Requesting: {url}")
    t0 = time.time()
    try:
        res = requests.get(url, timeout=5.0)
        t1 = time.time()
        print(f"Status Code: {res.status_code}")
        print(f"Time Taken: {t1 - t0:.3f} seconds")
    except Exception as e:
        print(f"Failed: {e}")
