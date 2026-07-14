with open('backend/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

proxy_code = '''
@app.get("/api/proxy/vworld")
def proxy_vworld(data: str, geomFilter: str, crs: str = "EPSG:4326"):
    import requests
    url = 'https://api.vworld.kr/req/data'
    params = {
        'service': 'data',
        'request': 'GetFeature',
        'data': data,
        'key': '2C1B6EA3-A71D-3294-9749-F878465C245B',
        'domain': 'localhost',
        'crs': crs,
        'geomFilter': geomFilter,
        'size': '1000'
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        return res.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}
'''

if 'proxy_vworld' not in text:
    text += proxy_code
    with open('backend/app.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Proxy added')
else:
    print('Proxy already exists')
