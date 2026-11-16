import requests
import urllib.parse
API_KEY = "876c80d2a9fd79ade2c9c2fea0d0d1b0657c4b4aadfc4917065326b6e7fa32b6"
SERVICE_KEY = urllib.parse.unquote(API_KEY)
API_URL = "https://apis.data.go.kr/B010003/OnbidRlstListSrvc2/getRlstCltrList2"

def check(region):
    params = {
        'serviceKey': SERVICE_KEY,
        'resultType': 'json',
        'numOfRows': 10,
        'pageNo': 1,
        'pvctTrgtYn': 'N',
        'prptDivCd': '0007,0010,0005,0004,0002,0003,0006,0008,0011,0013',
        'lctnSdnm': region
    }
    try:
        res = requests.get(API_URL, params=params)
        data = res.json()
        print(f"{region}: {len(data.get('body', {}).get('items', {}).get('item', []))} items found")
    except Exception as e:
        print(f"{region} error: {e}")

check("강원도")
check("강원특별자치도")
check("서울특별시")
