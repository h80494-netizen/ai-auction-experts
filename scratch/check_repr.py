import requests
import urllib.parse
import json

base_url = "https://raw.githubusercontent.com/raqoon886/Local_HangJeongDong/master/"
filename = "hangjeongdong_서울특별시.geojson"

encoded_filename = urllib.parse.quote(filename)
url = base_url + encoded_filename

r = requests.get(url)
content = r.content

# Let's check repr of first feature's properties decoded in utf-8
data = json.loads(content.decode('utf-8'))
prop = data['features'][0]['properties']
print("UTF-8 repr of adm_nm:", repr(prop.get('adm_nm')))
print("UTF-8 repr of sggnm:", repr(prop.get('sggnm')))
print("UTF-8 repr of sidonm:", repr(prop.get('sidonm')))
