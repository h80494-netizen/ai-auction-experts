import requests

API_KEY = '2C1B6EA3-A71D-3294-9749-F878465C245B'
url = "http://api.vworld.kr/req/data"
lon = 126.68484
lat = 37.461645

params = {
    "key": API_KEY,
    "service": "data",
    "request": "GetFeature",
    "data": "LP_PA_CBND_BUBUN",
    "geomFilter": f"POINT({lon} {lat})",
    "geometry": "false",
    "size": "1",
    "crs": "EPSG:4326"
}

print("Testing with crs=EPSG:4326")
res = requests.get(url, params=params).json()
print(res)

params.pop("crs")
print("\nTesting without crs")
res = requests.get(url, params=params).json()
print(res)
