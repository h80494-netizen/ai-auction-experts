import requests

base_url = "http://localhost:8000"

try:
    url = f"{base_url}/api/map/redevelopment_zones?min_lat=37.4&max_lat=37.6&min_lng=126.9&max_lng=127.1"
    r = requests.get(url)
    data = r.json()
    with open("scratch/api_dev_out.txt", "w", encoding="utf-8") as f:
        f.write(f"Count: {len(data['data'])}\n")
        for item in data['data'][:10]:
            f.write(f"{item['id']}: {item['name']}\n")
    print("Wrote Redevelopment API sample to scratch/api_dev_out.txt")
except Exception as e:
    print("Error:", e)

try:
    url = f"{base_url}/api/map/zoning?min_lat=37.4&max_lat=37.6&min_lng=126.9&max_lng=127.1"
    r = requests.get(url)
    data = r.json()
    with open("scratch/api_zone_out.txt", "w", encoding="utf-8") as f:
        f.write(f"Count: {len(data['data'])}\n")
        for item in data['data'][:10]:
            f.write(f"{item['id']}: {item['name']}\n")
    print("Wrote Zoning API sample to scratch/api_zone_out.txt")
except Exception as e:
    print("Error:", e)
