import requests
import urllib.parse

base_url = "https://raw.githubusercontent.com/raqoon886/Local_HangJeongDong/master/"
filename = "hangjeongdong_서울특별시.geojson"

encoded_filename = urllib.parse.quote(filename)
url = base_url + encoded_filename
print("Downloading from:", url)

try:
    r = requests.get(url, timeout=10)
    print("Status:", r.status_code)
    if r.status_code == 200:
        data = r.json()
        print("Success! Number of features:", len(data.get('features', [])))
        if len(data.get('features', [])) > 0:
            print("First feature properties:", data['features'][0]['properties'])
    else:
        print("Error content:", r.text[:200])
except Exception as e:
    print("Download failed:", e)
