import requests

url = "https://sbiz.gmr.or.kr/gis/comm/wms.do"

cookies = {
    'JSESSIONID': 'E2E968C508982563FDC59DE10AB8AF26.node1',
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
    # Note standard stdr and flag
    'VIEWPARAMS': 'stdr:20253;flag:time;val:20;radius:100;',
    'STORE': 'gmr_new',
    'SRS': 'EPSG:3857', # Request standard Web Mercator
    'WIDTH': '512',
    'HEIGHT': '512',
    # Suwon coordinates in EPSG:3857
    'BBOX': '14138000,4473000,14143000,4478000'
}

try:
    print("Testing WMS GetMap with EPSG:3857 reprojection...")
    response = requests.get(url, cookies=cookies, headers=headers, params=params, timeout=10)
    print("Status Code:", response.status_code)
    print("Content-Type:", response.headers.get('Content-Type'))
    print("Length of response:", len(response.content))
    
    if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
        with open("scratch/gmr_wms_reproject_tile.png", "wb") as f:
            f.write(response.content)
        print("Success! Reprojected image saved as scratch/gmr_wms_reproject_tile.png")
    else:
        print("Response text snippet:")
        print(response.text[:1000])
except Exception as e:
    print("Error:", e)
