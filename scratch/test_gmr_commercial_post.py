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

params = {
    'SERVICE': 'WMS',
    'VERSION': '1.1.1',
    'REQUEST': 'GetMap',
    'FORMAT': 'image/png',
    'TRANSPARENT': 'true',
    'STYLES': '',
    'LAYERS': 'vw_gis_commercial_area',
    'STORE': 'gmr_new',
    'SRS': 'EPSG:5181',
    'WIDTH': '256',
    'HEIGHT': '256',
    # Suwon coordinates BBOX in EPSG:5181
    'BBOX': '200000,420000,205000,425000'
}

try:
    print("Testing GetMap for vw_gis_commercial_area with POST...")
    resp = requests.post(url, headers=headers, data=params, timeout=10)
    print("Status Code:", resp.status_code)
    print("Content-Type:", resp.headers.get("Content-Type"))
    print("Content-Length:", resp.headers.get("Content-Length"))
    print("Bytes Length:", len(resp.content))
    if resp.status_code == 200 and 'image' in resp.headers.get("Content-Type", ""):
        with open("scratch/commercial_tile.png", "wb") as f:
            f.write(resp.content)
        print("Success! Saved commercial_tile.png")
    else:
        print("Response text:", resp.text[:500])
except Exception as e:
    print("Error:", e)
