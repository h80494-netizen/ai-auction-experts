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
    'VERSION': '1.1.0',
    'REQUEST': 'GetMap',
    'FORMAT': 'image/png',
    'TRANSPARENT': 'true',
    'STYLES': '',
    'LAYERS': 'vw_gis_pop_road',
    'VIEWPARAMS': 'stdr:20253;flag:time;val:20;to:5181;from:5181;xmin:203923.43052598886;ymin:421134.9184490329;xmax:204583.43052598886;ymax:421791.9184490329;radius:100;',
    'STORE': 'gmr_new',
    'SRS': 'EPSG:5181',
    'WIDTH': '660',
    'HEIGHT': '657',
    'BBOX': '203923.43052598886,421134.9184490329,204583.43052598886,421791.9184490329'
}

try:
    print("Requesting WMS GetMap image from GMR...")
    response = requests.get(url, cookies=cookies, headers=headers, params=params, timeout=10)
    print("Status Code:", response.status_code)
    print("Content-Type:", response.headers.get('Content-Type'))
    print("Length of response:", len(response.content))
    
    # Save the PNG image
    if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
        with open("scratch/gmr_wms_tile.png", "wb") as f:
            f.write(response.content)
        print("Success! Image saved as scratch/gmr_wms_tile.png")
    else:
        print("Response text snippet (if not image):")
        print(response.text[:1000])
except Exception as e:
    print("Error:", e)
