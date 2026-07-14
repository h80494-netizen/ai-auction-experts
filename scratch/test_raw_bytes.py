import requests
import urllib.parse

base_url = "https://raw.githubusercontent.com/raqoon886/Local_HangJeongDong/master/"
filename = "hangjeongdong_서울특별시.geojson"

encoded_filename = urllib.parse.quote(filename)
url = base_url + encoded_filename

r = requests.get(url)
print("Content-Type:", r.headers.get('Content-Type'))
print("First 500 bytes of raw content:")
print(r.content[:500])
