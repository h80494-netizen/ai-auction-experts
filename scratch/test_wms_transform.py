import requests
from pyproj import Transformer

url = "https://sbiz.gmr.or.kr/gis/comm/wms.do"

# Exact working cookie from the user
cookies = {
    'JSESSIONID': '6CBAAE871930F767944F9D869813D60A.node1',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Referer': 'https://sbiz.gmr.or.kr/map/myStore.do',
    'Origin': 'https://sbiz.gmr.or.kr',
}

# Example coordinates from 수원 (approximate) in EPSG:3857
minx, miny, maxx, maxy = 14138000, 4473000, 14143000, 4478000

# Transformer from EPSG:3857 to EPSG:5181
transformer = Transformer.from_crs("EPSG:3857", "EPSG:5181", always_xy=True)
gmr_minx, gmr_miny = transformer.transform(minx, miny)
gmr_maxx, gmr_maxy = transformer.transform(maxx, maxy)

print(f"Transformed coords to EPSG:5181:")
print(f"  xmin: {gmr_minx}, ymin: {gmr_miny}")
print(f"  xmax: {gmr_maxx}, ymax: {gmr_maxy}")

params = {
    'SERVICE': 'WMS',
    'VERSION': '1.1.0',
    'REQUEST': 'GetMap',
    'FORMAT': 'image/png',
    'TRANSPARENT': 'true',
    'STYLES': '',
    'LAYERS': 'vw_gis_pop_road',
    # Note standard stdr and flag, with reprojected xmin, ymin, xmax, ymax
    'VIEWPARAMS': f'stdr:20253;flag:time;val:20;to:5181;from:5181;xmin:{gmr_minx};ymin:{gmr_miny};xmax:{gmr_maxx};ymax:{gmr_maxy};radius:100;',
    'STORE': 'gmr_new',
    'SRS': 'EPSG:5181',
    'WIDTH': '256',
    'HEIGHT': '256',
    'BBOX': f"{gmr_minx},{gmr_miny},{gmr_maxx},{gmr_maxy}"
}

try:
    print("\nRequesting GMR WMS tile via coordinate transformation...")
    response = requests.get(url, cookies=cookies, headers=headers, params=params, timeout=10)
    print("Status Code:", response.status_code)
    print("Content-Type:", response.headers.get('Content-Type'))
    print("Length of response content:", len(response.content))
    
    if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
        with open("scratch/transformed_tile.png", "wb") as f:
            f.write(response.content)
        print("Success! Image saved as scratch/transformed_tile.png")
    else:
        print("Response text (first 500 chars):")
        print(response.text[:500])
except Exception as e:
    print("Error:", e)
