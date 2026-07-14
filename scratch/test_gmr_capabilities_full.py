import requests
import re

url = "https://sbiz.gmr.or.kr/gis/comm/wms.do"
cookie_str = "_ga=GA1.1.1448596582.1779619476; JSESSIONID=6CBAAE871930F767944F9D869813D60A.node1; _ga_5WT2XJMPB5=GS2.1.s1779665383$o2$g1$t1779665394$j49$l0$h0"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Referer': 'https://sbiz.gmr.or.kr/map/trdArea.do',
    'Origin': 'https://sbiz.gmr.or.kr',
    'Cookie': cookie_str
}

params = {
    'SERVICE': 'WMS',
    'VERSION': '1.1.1',
    'REQUEST': 'GetCapabilities'
}

print("--- Testing GET request ---")
try:
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    print("GET Status:", resp.status_code)
    print("GET Headers:", dict(resp.headers))
    print("GET Length:", len(resp.content))
    if len(resp.content) > 100:
        print("Snippet:", resp.text[:500])
except Exception as e:
    print("GET Error:", e)

print("\n--- Testing POST request ---")
try:
    resp = requests.post(url, headers=headers, data=params, timeout=10)
    print("POST Status:", resp.status_code)
    print("POST Headers:", dict(resp.headers))
    print("POST Length:", len(resp.content))
    if len(resp.content) > 100:
        print("Snippet:", resp.text[:500])
        with open("scratch/gmr_capabilities_post.xml", "w", encoding="utf-8") as f:
            f.write(resp.text)
        layers = re.findall(r'<Name>([^<]+)</Name>', resp.text)
        titles = re.findall(r'<Title>([^<]+)</Title>', resp.text)
        print("\nFound Layers:")
        for name, title in zip(layers, titles):
            print(f"  Name: {name} | Title: {title}")
except Exception as e:
    print("POST Error:", e)
