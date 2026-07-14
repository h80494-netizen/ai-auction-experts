import urllib.request
import json

def main():
    url = "http://localhost:8000/api/map/crosswalks?min_lat=37.48&max_lat=37.49&min_lng=126.99&max_lng=127.00"
    try:
        response = urllib.request.urlopen(url)
        data = response.read().decode('utf-8')
        res_json = json.loads(data)
        print("API Response status:", res_json.get("status"))
        features = res_json.get("data", {}).get("features", [])
        print("Number of features returned:", len(features))
        if features:
            print("First feature sample:", features[0])
    except Exception as e:
        print("Error calling API:", e)

if __name__ == '__main__':
    main()
