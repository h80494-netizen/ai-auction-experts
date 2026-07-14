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

# Let's try querying List endpoint for cityRecyBsnsGb: 1 (정비사업) and 2 (택지개발?) or other combinations
# Standard Spring MVC lists take paging parameters like pIndex, pSize, pageIndex, etc., or sigungu code sggCd
data = {
    'sggCd': '00000', # 00000 means all sigungu in Gyeonggi
    'cityRecyBsnsGb': '1', # 1 for 정비사업
    'pageIndex': '1',
    'recordCountPerPage': '100'
}

url = 'https://gris.gg.go.kr/dev/city/selectCityRecyBsnsList.do'
try:
    print(f"Testing GRIS List URL: {url}")
    res = requests.post(url, cookies=cookies, headers=headers, data=data, timeout=10)
    print("Status Code:", res.status_code)
    print("Content-Type:", res.headers.get("Content-Type"))
    
    # Try printing raw JSON or first 1000 characters
    try:
        res_json = res.json()
        print("Response is valid JSON!")
        print(json.dumps(res_json, indent=2, ensure_ascii=False)[:2000])
        if "list" in res_json or "resultList" in res_json:
            items = res_json.get("list", res_json.get("resultList", []))
            print(f"Number of items returned: {len(items)}")
    except Exception as je:
        print("JSON parse failed, printing raw response text:")
        print(res.text[:1000])
except Exception as e:
    print("Error:", e)
