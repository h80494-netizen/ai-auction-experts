import requests

url = "http://localhost:8000/api/map/auctions?min_lat=37.4&max_lat=37.6&min_lng=126.5&max_lng=127.2&regions=서울"
try:
    res = requests.get(url).json()
    auctions = res.get("data", [])
    print(f"Total auctions returned: {len(auctions)}")
    if auctions:
        print("First 5 auction case numbers from API:")
        for a in auctions[:5]:
            print(f" - {repr(a.get('case_no'))}")
except Exception as e:
    print("Error:", e)
