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

# Parameters for EPSG:5181 (from scratch/test_gmr_latest.py)
params_5181 = {
    'SERVICE': 'WMS',
    'VERSION': '1.1.1',
    'REQUEST': 'GetMap',
    'FORMAT': 'image/png',
    'TRANSPARENT': 'true',
    'STYLES': '',
    'LAYERS': 'vw_gis_pop_road',
    'VIEWPARAMS': 'stdr:20253;flag:time;val:20;radius:100;to:5181;from:5181;xmin:203923.43052598886;ymin:421134.9184490329;xmax:204583.43052598886;ymax:421791.9184490329;',
    'STORE': 'gmr_new',
    'SRS': 'EPSG:5181',
    'WIDTH': '660',
    'HEIGHT': '657',
    'BBOX': '203923.43052598886,421134.9184490329,204583.43052598886,421791.9184490329'
}

print("=== Testing GetMap with POST ===")
try:
    resp = requests.post(url, headers=headers, data=params_5181, timeout=10)
    print("Status:", resp.status_code)
    print("Content-Type:", resp.headers.get("Content-Type"))
    print("Content-Length:", resp.headers.get("Content-Length"))
    print("Bytes Length:", len(resp.content))
    if len(resp.content) > 100:
        with open("scratch/post_tile.png", "wb") as f:
            f.write(resp.content)
        print("Success! Saved post_tile.png")
    else:
        print("Response text:", resp.text[:500])
except Exception as e:
    print("Error:", e)
