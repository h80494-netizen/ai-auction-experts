import requests

url = "http://127.0.0.1:8000/api/gmr/wms"

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
    print("Testing GMR WMS Proxy response details...")
    response = requests.get(url, params=params, timeout=5)
    print("Status Code:", response.status_code)
    print("Response Headers:", dict(response.headers))
    print("Length of content:", len(response.content))
except Exception as e:
    print("Error:", e)
