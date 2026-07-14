import requests

c_min_lat, c_min_lng = 37.50, 127.03
c_max_lat, c_max_lng = 37.51, 127.04

query = f"""
[out:json];
way({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng});
out geom 5;
"""

url = "https://overpass.kumi.systems/api/interpreter"
try:
    response = requests.post(url, data={"data": query}, timeout=10.0)
    print("Status code:", response.status_code)
    if response.status_code == 200:
        data = response.json()
        elements = data.get("elements", [])
        print("Number of elements:", len(elements))
        if elements:
            print("Sample element:", elements[0])
    else:
        print("Error output:", response.text[:200])
except Exception as e:
    print("Failed to query:", e)
