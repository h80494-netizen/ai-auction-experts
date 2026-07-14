import urllib.request
import json

url = "http://localhost:8000/api/map/redevelopment_zones?min_lat=37.470&max_lat=37.480&min_lng=126.630&max_lng=126.640"
print(f"Testing URL: {url}")
try:
    response = urllib.request.urlopen(url, timeout=5)
    res_data = json.loads(response.read().decode('utf-8'))
    print("Status:", res_data.get("status"))
    if res_data.get("status") == "success":
        data = res_data.get("data", [])
        print(f"Number of zones returned: {len(data)}")
        if data:
            print("First item sample:")
            print("ID:", data[0].get("id"))
            print("Name:", data[0].get("name"))
            print("Propel Code:", data[0].get("propel_cd"))
            print("GeoJSON (truncated):", data[0].get("geojson")[:100])
        else:
            print("WARNING: 0 items returned.")
    else:
        print("ERROR: Response status failed")
except Exception as e:
    print("ERROR querying local server:", e)
