import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

def get_session_cookies():
    try:
        main_url = 'https://www.dooinauction.com/ca/caList.php?srchHistory=16'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
        }
        session.get(main_url, headers=headers, timeout=10)
        return session.cookies.get_dict()
    except Exception as e:
        return {'PHPSESSID': '15fbf4849ecd7ff4bd2678c3c6bd0475'}

cookies = get_session_cookies()

def check_region(sicd, name):
    params = {
        'dataSize': '20',
        'pageNo': '1',
        'stat': '11',
        'siCd': str(sicd),
        'srchCase': 'srchAll',
    }
    url = 'https://www.dooinauction.com/ca/res/AuctList.php'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    response = session.get(url, params=params, cookies=cookies, headers=headers)
    if response.status_code == 200:
        try:
            data = response.json()
            cnt = data.get('totalCnt', 0)
            print(f"{name}({sicd}): {cnt}개")
        except:
            print(f"{name}({sicd}): JSON Error, text: {response.text[:100]}")
    else:
        print(f"{name}({sicd}): Error {response.status_code}")

check_region(11, '서울')
check_region(41, '경기')
check_region(28, '인천')
check_region(42, '강원')
check_region(51, '강원(51?)')
check_region(32, '강원(32?)')
check_region(31, '경북?')
check_region(33, '경남?')
check_region(52, '전북?')
check_region(53, '전남?')
check_region(43, '충북?')
check_region(44, '충남?')
