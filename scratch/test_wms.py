import requests
url = 'https://api.vworld.kr/req/wms'

layers_to_test = [
    'lt_c_upisctrq', 'lt_c_upisdq3', 'lt_c_upisdq6', 
    'lt_c_upisdq4', 'lt_c_upisigq', 'lt_c_upisdq1', 'lt_c_upisdq2',
    'lt_c_uq111'
]

for layer in layers_to_test:
    params = {
        'SERVICE': 'WMS',
        'REQUEST': 'GetMap',
        'VERSION': '1.3.0',
        'LAYERS': layer,
        'STYLES': '',
        'FORMAT': 'image/png',
        'TRANSPARENT': 'true',
        'CRS': 'EPSG:3857',
        'BBOX': '14138127.351239845,4507399.704044949,14143019.310618037,4512291.663423141',
        'WIDTH': '256',
        'HEIGHT': '256',
        'KEY': '2C1B6EA3-A71D-3294-9749-F878465C245B',
        'DOMAIN': 'localhost'
    }
    try:
        res = requests.get(url, params=params, timeout=5)
        if 'xml' in res.headers.get('Content-Type', ''):
            print(f'{layer}: Failed (XML Error returned)')
        else:
            print(f'{layer}: Success! Size: {len(res.content)}')
    except Exception as e:
        print(f'{layer}: Error {e}')
