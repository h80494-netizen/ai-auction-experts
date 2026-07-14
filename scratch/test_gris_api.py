import requests
import json

cookies = {
    'PHAROSVISITOR': '000067c7019e7eedaea9355769006fbb',
    'JSESSIONID': 'Hd1kgLwfHaw0193HnjAb0o0x1jOQZBsZUR6r0d97ItzvRHaGTA7ywP0KQ3y5CFYg.amV1c19kb21haW4vc2VydmVyNV8y',
    '_ga': 'GA1.1.1842750864.1780245973',
    '_ga_MN1SDDDMMK': 'GS2.1.s1780245972$o1$g1$t1780246154$j53$l0$h0',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ru;q=0.6',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://gris.gg.go.kr',
    'Referer': 'https://gris.gg.go.kr/map/main/grisMapView.do',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

# Try fetching detail for seq 337
data = {
    'seq': '337',
    'sggCd': '00000',
    'cityRecyBsnsGb': '1', # 1 might mean 도시개발 or 정비사업?
}

try:
    print("Testing GRIS API for seq 337...")
    res = requests.post('https://gris.gg.go.kr/dev/city/selectCityRecyBsnsDetail.do', cookies=cookies, headers=headers, data=data, timeout=10)
    print("Status Code:", res.status_code)
    print("Headers:", dict(res.headers))
    content_type = res.headers.get("Content-Type", "")
    
    if "json" in content_type or res.text.strip().startswith("{"):
        try:
            res_json = res.json()
            print("Response is valid JSON!")
            print(json.dumps(res_json, indent=2, ensure_ascii=False)[:1000])
        except Exception as je:
            print("JSON parse failed, printing first 500 chars of text:")
            print(res.text[:500])
    else:
        print("Response is HTML or other text:")
        print(res.text[:1000])
except Exception as e:
    print("Error querying GRIS:", e)
