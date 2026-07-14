import requests

url = "https://sbiz.gmr.or.kr/gis/comm/wms.do"
cookie_str = "_ga=GA1.1.1448596582.1779619476; JSESSIONID=6CBAAE871930F767944F9D869813D60A.node1; _ga_5WT2XJMPB5=GS2.1.s1779665383$o2$g1$t1779665394$j49$l0$h0"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Referer': 'https://sbiz.gmr.or.kr/map/trdArea.do',
    'Origin': 'https://sbiz.gmr.or.kr',
    'Cookie': cookie_str,
    'Content-Type': 'application/x-www-form-urlencoded'
}

params_gmr = {
    'SERVICE': 'WMS',
    'VERSION': '1.1.1',
    'REQUEST': 'GetMap',
    'FORMAT': 'image/png',
    'TRANSPARENT': 'true',
    'STYLES': '',
    'LAYERS': 'vw_gis_commercial_area',
    'STORE': 'gmr',  # Try store 'gmr'
    'SRS': 'EPSG:5181',
    'WIDTH': '256',
    'HEIGHT': '256',
    'BBOX': '203923.43052598886,421134.9184490329,204583.43052598886,421791.9184490329'
}

params_gmr_new = params_gmr.copy()
params_gmr_new['STORE'] = 'gmr_new'

print("--- Testing with STORE='gmr' ---")
try:
    resp = requests.post(url, headers=headers, data=params_gmr, timeout=10)
    print("Status:", resp.status_code)
    print("Content-Type:", resp.headers.get("Content-Type"))
    print("Length:", len(resp.content))
except Exception as e:
    print("Error gmr:", e)

print("\n--- Testing with STORE='gmr_new' ---")
try:
    resp = requests.post(url, headers=headers, data=params_gmr_new, timeout=10)
    print("Status:", resp.status_code)
    print("Content-Type:", resp.headers.get("Content-Type"))
    print("Length:", len(resp.content))
except Exception as e:
    print("Error gmr_new:", e)
