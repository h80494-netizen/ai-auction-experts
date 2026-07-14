import requests

url = "https://sbiz.gmr.or.kr/gis/comm/wms.do"

cookies = {
    'JSESSIONID': '6CBAAE871930F767944F9D869813D60A.node1',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Referer': 'https://sbiz.gmr.or.kr/map/myStore.do',
    'Origin': 'https://sbiz.gmr.or.kr',
}

params = {
    'SERVICE': 'WMS',
    'VERSION': '1.1.0',
    'REQUEST': 'GetCapabilities'
}

try:
    print("Requesting GMR WMS GetCapabilities...")
    response = requests.get(url, cookies=cookies, headers=headers, params=params, timeout=15)
    print("Status Code:", response.status_code)
    print("Content-Length:", len(response.content))
    
    xml_content = response.text
    # Save the capabilities XML to check its layers
    with open("scratch/gmr_capabilities.xml", "w", encoding="utf-8") as f:
        f.write(xml_content)
    print("Saved capabilities XML to scratch/gmr_capabilities.xml")
    
    # Parse layer names using simple string parsing or regex
    import re
    layers = re.findall(r'<Name>([^<]+)</Name>', xml_content)
    titles = re.findall(r'<Title>([^<]+)</Title>', xml_content)
    
    print("\nFound Layer Names and Titles:")
    for name, title in zip(layers, titles):
        print(f"  Name: {name} | Title: {title}")
        
except Exception as e:
    print("Error:", e)
