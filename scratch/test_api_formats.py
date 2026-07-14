import requests

API_KEY = '2C1B6EA3-A71D-3294-9749-F878465C245B'
url = "http://api.vworld.kr/req/data"
lon = 126.68484
lat = 37.461645

def test_geom(gf):
    params = {
        "key": API_KEY,
        "service": "data",
        "request": "GetFeature",
        "data": "LP_PA_CBND_BUBUN",
        "geomFilter": gf,
        "geometry": "false",
        "size": "1"
    }
    res = requests.get(url, params=params).json()
    print(f"geomFilter={gf} -> {res.get('status')}, error={res.get('response',{}).get('error',{}).get('text')}")

test_geom("box(126,37,127,38)")
test_geom(f"box({lon-0.0001},{lat-0.0001},{lon+0.0001},{lat+0.0001})")
test_geom(f"POINT({lon} {lat})")
test_geom(f"point({lon} {lat})")
test_geom(f"POINT({lon}, {lat})")
