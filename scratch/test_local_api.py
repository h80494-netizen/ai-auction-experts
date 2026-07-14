import requests

base_url = "http://localhost:8000"

# Test Redevelopment API
try:
    url = f"{base_url}/api/map/redevelopment_zones?min_lat=37.4&max_lat=37.6&min_lng=126.9&max_lng=127.1"
    r = requests.get(url)
    data = r.json()
    print("Redevelopment Zones API status:", data.get('status'))
    print("Redevelopment Zones API count:", len(data.get('data', [])))
    if data.get('data'):
        print("Sample zone name:", data['data'][0]['name'])
except Exception as e:
    print("Error querying Redevelopment API:", e)

# Test Zoning API
try:
    url = f"{base_url}/api/map/zoning?min_lat=37.4&max_lat=37.6&min_lng=126.9&max_lng=127.1"
    r = requests.get(url)
    data = r.json()
    print("\nZoning API status:", data.get('status'))
    print("Zoning API count:", len(data.get('data', [])))
    if data.get('data'):
        print("Sample zoning name:", data['data'][0]['name'])
except Exception as e:
    print("Error querying Zoning API:", e)

# Test Planning Roads API
try:
    url = f"{base_url}/api/map/planning_roads?min_lat=37.4&max_lat=37.6&min_lng=126.9&max_lng=127.1"
    r = requests.get(url)
    data = r.json()
    print("\nPlanning Roads API status:", data.get('status'))
    print("Planning Roads API count:", len(data.get('data', [])))
    if data.get('data'):
        print("Sample planning road name:", data['data'][0]['name'])
except Exception as e:
    print("Error querying Planning Roads API:", e)
