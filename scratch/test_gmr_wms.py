import requests

urls = [
    "https://sbiz.gmr.or.kr/gis/wms.do",
    "https://sbiz.gmr.or.kr/gis/wfs.do",
    "https://sbiz.gmr.or.kr/gis/comm/wms.do",
    "https://sbiz.gmr.or.kr/gis/comm/wfs.do",
    "https://sbiz.gmr.or.kr/gis/map/wms.do",
    "https://sbiz.gmr.or.kr/gis/wms.json",
    "https://sbiz.gmr.or.kr/gis/wfs.json",
]

cookies = {
    'JSESSIONID': 'E2E968C508982563FDC59DE10AB8AF26.node1',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
}

for url in urls:
    try:
        response = requests.get(url, cookies=cookies, headers=headers, timeout=5)
        print(f"URL: {url}")
        print(f"  Status Code: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
        print(f"  Snippet: {response.text[:200].strip()}")
        print("-" * 50)
    except Exception as e:
        print(f"URL: {url} Error: {e}")
