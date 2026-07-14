import requests

url = "https://sbiz.gmr.or.kr/gis/comm/wms.do"

# Use the exact cookie string provided by the user
cookie_str = "_ga=GA1.1.1448596582.1779619476; JSESSIONID=6CBAAE871930F767944F9D869813D60A.node1; _ga_5WT2XJMPB5=GS2.1.s1779665383$o2$g1$t1779665394$j49$l0$h0"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Referer': 'https://sbiz.gmr.or.kr/map/myStore.do',
    'Origin': 'https://sbiz.gmr.or.kr',
    'Cookie': cookie_str
}

params_5181 = {
    'SERVICE': 'WMS',
    'VERSION': '1.1.1',
    'REQUEST': 'GetMap',
    'FORMAT': 'image/png',
    'TRANSPARENT': 'true',
    'STYLES': '',
    'LAYERS': 'vw_gis_pop_road',
    'VIEWPARAMS': 'stdr:20253;flag:time;val:20;radius:100;',
    'STORE': 'gmr_new',
    'SRS': 'EPSG:5181',
    'WIDTH': '660',
    'HEIGHT': '657',
    'BBOX': '203923.43052598886,421134.9184490329,204583.43052598886,421791.9184490329'
}

params_3857 = {
    'SERVICE': 'WMS',
    'VERSION': '1.1.1',
    'REQUEST': 'GetMap',
    'FORMAT': 'image/png',
    'TRANSPARENT': 'true',
    'STYLES': '',
    'LAYERS': 'vw_gis_pop_road',
    'VIEWPARAMS': 'stdr:20253;flag:time;val:20;radius:100;',
    'STORE': 'gmr_new',
    'SRS': 'EPSG:3857',
    'WIDTH': '256',
    'HEIGHT': '256',
    'BBOX': '14138000,4473000,14143000,4478000'
}

print("=== Testing EPSG:5181 with Full Cookie & Referer ===")
try:
    resp = requests.get(url, headers=headers, params=params_5181, timeout=10)
    print("Status:", resp.status_code)
    print("Content-Type:", resp.headers.get("Content-Type"))
    print("Content-Length:", resp.headers.get("Content-Length"))
    print("Content Bytes Length:", len(resp.content))
    if len(resp.content) > 0 and 'image' in resp.headers.get("Content-Type", ""):
        with open("scratch/latest_5181.png", "wb") as f:
            f.write(resp.content)
        print("Successfully saved EPSG:5181 tile!")
    else:
        print("Text preview:", resp.text[:300])
except Exception as e:
    print("Error 5181:", e)

print("\n=== Testing EPSG:3857 with Full Cookie & Referer ===")
try:
    resp = requests.get(url, headers=headers, params=params_3857, timeout=10)
    print("Status:", resp.status_code)
    print("Content-Type:", resp.headers.get("Content-Type"))
    print("Content-Length:", resp.headers.get("Content-Length"))
    print("Content Bytes Length:", len(resp.content))
    if len(resp.content) > 0 and 'image' in resp.headers.get("Content-Type", ""):
        with open("scratch/latest_3857.png", "wb") as f:
            f.write(resp.content)
        print("Successfully saved EPSG:3857 tile!")
    else:
        print("Text preview:", resp.text[:300])
except Exception as e:
    print("Error 3857:", e)
