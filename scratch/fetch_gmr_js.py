import requests
import re

cookie_str = "_ga=GA1.1.1448596582.1779619476; JSESSIONID=6CBAAE871930F767944F9D869813D60A.node1; _ga_5WT2XJMPB5=GS2.1.s1779665383$o2$g1$t1779665394$j49$l0$h0"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Referer': 'https://sbiz.gmr.or.kr/map/trdArea.do',
    'Origin': 'https://sbiz.gmr.or.kr',
    'Cookie': cookie_str
}

urls = [
    'https://sbiz.gmr.or.kr/js/map/trdarea/trdarea.js',
    'https://sbiz.gmr.or.kr/js/map/commonui.js',
    'https://sbiz.gmr.or.kr/js/gmr/common/common.js'
]

for url in urls:
    try:
        print(f"Fetching {url}...")
        resp = requests.get(url, headers=headers, timeout=10)
        print("  Status:", resp.status_code)
        if resp.status_code == 200:
            print("  Length:", len(resp.text))
            filename = url.split('/')[-1]
            if '.js' not in filename:
                filename += '.js'
            with open(f"scratch/{filename}", "w", encoding="utf-8") as f:
                f.write(resp.text)
                
            # Search for layers, vw_gis_, store, wms, etc.
            vw_matches = re.findall(r'vw_gis_[a-zA-Z0-9_]+', resp.text)
            if vw_matches:
                print("  vw_gis_ matches:", set(vw_matches))
            else:
                print("  No vw_gis_ matches.")
                
            # Print any references to wms layers or stores
            store_matches = re.findall(r'store\s*:\s*[\'"][^\'"]+[\'"]', resp.text, re.IGNORECASE)
            if store_matches:
                print("  Store matches:", set(store_matches))
                
    except Exception as e:
        print("  Error:", e)
