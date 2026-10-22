import sys
import os
import requests

# Include backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sgis_service import sgis_service

print("1. Testing Auth...")
sys.stdout.flush()
token = sgis_service.get_access_token()
print("Token:", token)
sys.stdout.flush()

if token:
    lat, lng = 37.4979, 127.0276
    x, y = sgis_service.transform_coords(lat, lng)
    # Round to integers
    x_int = int(round(x))
    y_int = int(round(y))
    print(f"UTM-K Coords: X={x_int}, Y={y_int}")
    sys.stdout.flush()
    
    # Let's test calling population.json for multiple years and print responses
    url = "https://sgisapi.kostat.go.kr/OpenAPI3/stats/population.json"
    for year in ["2021", "2020", "2019"]:
        params = {
            "accessToken": token,
            "year": year,
            "area_type": "1",
            "x": str(x_int),
            "y": str(y_int),
            "r": "1000"
        }
        try:
            print(f"Trying year {year}...")
            sys.stdout.flush()
            res = requests.get(url, params=params, timeout=5)
            print(f"Status: {res.status_code}")
            print(f"Response: {res.text[:300]}")
            sys.stdout.flush()
        except Exception as e:
            print(f"Error for year {year}: {e}")
            sys.stdout.flush()
else:
    print("Auth Failed")
    sys.stdout.flush()
