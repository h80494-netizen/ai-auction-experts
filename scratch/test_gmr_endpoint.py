import requests

url = "https://sbiz.gmr.or.kr/gis/comm/fac.json"

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

# Empty data first to see if it complains or gives a clue
data = {}

try:
    print(f"Sending POST to {url}...")
    response = requests.post(url, headers=headers, data=data, timeout=10)
    print("Status Code:", response.status_code)
    print("Headers:", dict(response.headers))
    print("Response text (first 1000 chars):")
    print(response.text[:1000])
except Exception as e:
    print("Error:", e)
