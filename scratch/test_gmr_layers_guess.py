import requests

url = "https://sbiz.gmr.or.kr/gis/comm/wms.do"
cookie_str = "_ga=GA1.1.1448596582.1779619476; JSESSIONID=6CBAAE871930F767944F9D869813D60A.node1; _ga_5WT2XJMPB5=GS2.1.s1779665383$o2$g1$t1779665394$j49$l0$h0"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Referer': 'https://sbiz.gmr.or.kr/map/trdArea.do',
    'Origin': 'https://sbiz.gmr.or.kr',
    'Cookie': cookie_str,
    'Content-Type': 'application/x-www-form-urlencoded'
}

# We will try a list of guessed layer names
guesses = [
    'vw_gis_pop_road',
    'vw_gis_trd_area',
    'vw_gis_trd_area_yn',
    'vw_gis_trdar',
    'vw_gis_trdar_area',
    'vw_gis_trd',
    'vw_gis_com_area',
    'vw_gis_commercial',
    'vw_gis_biz_area',
    'vw_gis_pop_grid',
    'vw_gis_road',
    'vw_gis_road_flow',
    'vw_gis_shangquan',
    
    # Try without vw_gis_
    'trd_area',
    'trdar',
    'pop_road',
    
    # Try with store name gmr_new
    'gmr_new:vw_gis_trd_area',
    'gmr_new:vw_gis_trdar',
    'gmr_new:vw_gis_trdar_area',
    'gmr_new:vw_gis_trd',
    'gmr_new:vw_gis_pop_road'
]

params = {
    'SERVICE': 'WMS',
    'VERSION': '1.1.1',
    'REQUEST': 'GetMap',
    'FORMAT': 'image/png',
    'TRANSPARENT': 'true',
    'STYLES': '',
    'VIEWPARAMS': 'stdr:20253;flag:time;val:20;radius:100;to:5181;from:5181;xmin:203923.43052598886;ymin:421134.9184490329;xmax:204583.43052598886;ymax:421791.9184490329;',
    'STORE': 'gmr_new',
    'SRS': 'EPSG:5181',
    'WIDTH': '256',
    'HEIGHT': '256',
    'BBOX': '203923.43052598886,421134.9184490329,204583.43052598886,421791.9184490329'
}

for layer in guesses:
    p = params.copy()
    p['LAYERS'] = layer
    try:
        resp = requests.post(url, headers=headers, data=p, timeout=5)
        content_type = resp.headers.get("Content-Type", "")
        length = len(resp.content)
        if resp.status_code == 200 and 'image' in content_type and length > 2000:
            print(f"[SUCCESS] Layer: '{layer}' is VALID! Content-Length: {length}, Content-Type: {content_type}")
        else:
            # Let's see the error snippet if it's an XML exception
            error_snippet = ""
            if 'xml' in content_type or 'html' in content_type:
                error_snippet = resp.text[:150].replace('\n', ' ').strip()
            print(f"[FAILED] Layer: '{layer}' | Status: {resp.status_code} | Content-Type: {content_type} | Length: {length} | Error: {error_snippet}")
    except Exception as e:
        print(f"[ERROR] Layer: '{layer}' | Exception: {e}")
