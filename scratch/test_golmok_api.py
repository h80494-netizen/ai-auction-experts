import requests
from pyproj import Transformer
import json

# Lat/Lng of Gangnam Station
lat, lng = 37.4979, 127.0276

# WGS84 (EPSG:4326) to Kakao Map projection (EPSG:5181)
transformer = Transformer.from_crs("EPSG:4326", "EPSG:5181", always_xy=True)

# Define bbox around Gangnam Station (about 300m)
min_lng, min_lat = lng - 0.003, lat - 0.003
max_lng, max_lat = lng + 0.003, lat + 0.003

minx, miny = transformer.transform(min_lng, min_lat)
maxx, maxy = transformer.transform(max_lng, max_lat)

print(f"WGS84 BBox: ({min_lat}, {min_lng}) to ({max_lat}, {max_lng})")
print(f"EPSG:5181 BBox: ({minx}, {miny}) to ({maxx}, {maxy})")

cookies = {
    'WL_PCID': '17664072624711807873154',
    'PCID': '17664073150776799552163',
    'JSESSIONID': 'rbeozm2xb1oOWaWYw8O51a20K6KaM172XfOirgiOOcqBVw11TYSGQrjBBaiYn1Pc.amV1c19kb21haW4vc2VvdWxjb3AxMDc=',
    'JSESSIONIDMOK': 'VWvym5eMPVQnO0KnYQPesf8OiGy96yslXeg2Giy1viq1d7xkTQCtlxu12yYXuU5B.amV1c19kb21haW4vZ29sbW9rMQ=='
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://golmok.seoul.go.kr',
    'Referer': 'https://golmok.seoul.go.kr/intendedOwner/intendedOwnerAnalysis.do',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

data = {
    'minx': str(minx),
    'miny': str(miny),
    'maxx': str(maxx),
    'maxy': str(maxy),
    'wkt': '',
    'dayweek': '1',
    'agrde': '00',
    'tmzon': '00',
    'ext': 'ext',
    'signguCd': '11'
}

try:
    print("Requesting fpop.json from Seoul Golmok API...")
    r = requests.post('https://golmok.seoul.go.kr/tool/wfs/fpop.json', cookies=cookies, headers=headers, data=data, timeout=5.0)
    print("Status Code:", r.status_code)
    print("Headers Content-Type:", r.headers.get('Content-Type'))
    
    # Try parsing json
    res_json = r.json()
    if isinstance(res_json, list):
        print(f"Response is a list of size {len(res_json)}. First 3 elements:")
        for idx, item in enumerate(res_json[:3]):
            print(f"[{idx}] {json.dumps(item, indent=2, ensure_ascii=False)}")
    else:
        print("Response is not a list. Type:", type(res_json))
        print(json.dumps(res_json, indent=2, ensure_ascii=False)[:2000])
        
except Exception as e:
    print("API Request Failed:", e)
