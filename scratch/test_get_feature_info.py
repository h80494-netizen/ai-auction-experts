import requests

url = "https://sbiz.gmr.or.kr/gis/comm/wms.do"

cookies = {
    'JSESSIONID': 'E2E968C508982563FDC59DE10AB8AF26.node1',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
}

# WMS GetFeatureInfo parameters
params = {
    'SERVICE': 'WMS',
    'VERSION': '1.1.0',
    'REQUEST': 'GetFeatureInfo',
    'FORMAT': 'image/png',
    'TRANSPARENT': 'true',
    'STYLES': '',
    'LAYERS': 'vw_gis_pop_road',
    'QUERY_LAYERS': 'vw_gis_pop_road', # Layer to query
    'VIEWPARAMS': 'stdr:20253;flag:time;val:20;to:5181;from:5181;xmin:203923.43052598886;ymin:421134.9184490329;xmax:204583.43052598886;ymax:421791.9184490329;radius:100;',
    'STORE': 'gmr_new',
    'SRS': 'EPSG:5181',
    'WIDTH': '660',
    'HEIGHT': '657',
    'BBOX': '203923.43052598886,421134.9184490329,204583.43052598886,421791.9184490329',
    'INFO_FORMAT': 'application/json', # Request JSON output
    'X': '330', # Middle of WIDTH
    'Y': '328', # Middle of HEIGHT
}

try:
    print("Requesting WMS GetFeatureInfo JSON from GMR...")
    response = requests.get(url, cookies=cookies, headers=headers, params=params, timeout=10)
    print("Status Code:", response.status_code)
    print("Content-Type:", response.headers.get('Content-Type'))
    print("Length of response:", len(response.text))
    print("Response text:")
    print(response.text[:2000])
except Exception as e:
    print("Error:", e)
