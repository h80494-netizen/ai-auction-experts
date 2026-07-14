import requests
import urllib.parse
import json

base_url = "https://raw.githubusercontent.com/raqoon886/Local_HangJeongDong/master/"
filename = "hangjeongdong_서울특별시.geojson"
url = base_url + urllib.parse.quote(filename)
r = requests.get(url)
data = r.json()

for feat in data['features']:
    adm_nm = feat['properties']['adm_nm']
    if "금호" in adm_nm or "성수" in adm_nm or "왕십리" in adm_nm:
        print("Feature adm_nm:", adm_nm, "sggnm:", feat['properties'].get('sggnm'))
