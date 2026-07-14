import requests

url = "https://sbiz.gmr.or.kr/gis/comm/wms.do"

cookies = {
    'JSESSIONID': '6CBAAE871930F767944F9D869813D60A.node1',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
}

params = {
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

try:
    print("Testing DIRECT WMS query to GMR with new cookie...")
    response = requests.get(url, cookies=cookies, headers=headers, params=params, timeout=10)
    print("Status Code:", response.status_code)
    print("Content-Type:", response.headers.get('Content-Type'))
    print("Length of content:", len(response.content))
    print("Response headers:", dict(response.headers))
    if 'image' not in response.headers.get('Content-Type', ''):
        print("Response text (first 500 chars):")
        print(response.text[:500])
    else:
        # Save to file to see if it's a valid PNG
        with open("scratch/direct_tile_new.png", "wb") as f:
            f.write(response.content)
        print("Image saved to scratch/direct_tile_new.png")
except Exception as e:
    print("Error:", e)
