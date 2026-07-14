import requests
from urllib.parse import unquote

url = "https://sbiz.gmr.or.kr/gis/comm/fac.json"

cookies = {
    'JSESSIONID': '6CBAAE871930F767944F9D869813D60A.node1',
    '_ga': 'GA1.1.1448596582.1779619476',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://sbiz.gmr.or.kr',
    'Referer': 'https://sbiz.gmr.or.kr/map/myStore.do',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

# Parse the user's payload string
payload_str = "from=5181&to=5181&proj=5181&extent=POLYGON((203923.43052598886+421134.9184490329%2C203923.43052598886+421791.9184490329%2C204583.43052598886+421791.9184490329%2C204583.43052598886+421134.9184490329%2C203923.43052598886+421134.9184490329))&tp=fac&val=101&sub="

# Build dict
data = {}
for part in payload_str.split('&'):
    if '=' in part:
        k, v = part.split('=', 1)
        data[k] = unquote(v).replace('+', ' ')

try:
    print("Sending POST request with user's Payload...")
    print("Data being sent:", data)
    response = requests.post(url, cookies=cookies, headers=headers, data=data, timeout=10)
    print("Status Code:", response.status_code)
    print("Content-Type:", response.headers.get('Content-Type'))
    print("Response text (first 2000 chars):")
    print(response.text[:2000])
except Exception as e:
    print("Error:", e)
