import requests
import urllib.parse

base_url = "https://raw.githubusercontent.com/raqoon886/Local_HangJeongDong/master/"
regions = ["서울특별시", "인천광역시", "경기도"]

for reg in regions:
    filename = f"hangjeongdong_{reg}.geojson"
    encoded_filename = urllib.parse.quote(filename)
    url = base_url + encoded_filename
    print(f"Testing {reg}...")
    try:
        r = requests.get(url, timeout=10)
        print("  Status:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            print("  Number of features:", len(data.get('features', [])))
        else:
            print("  Error content size:", len(r.text))
    except Exception as e:
        print("  Failed:", e)
