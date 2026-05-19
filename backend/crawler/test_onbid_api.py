import requests

API_KEY = "f3a15815abecaa938c1aae6a9a9a792bb32efd06c2af0be789a7aae0d92eb9f9"

url = "http://apis.data.go.kr/B551505/kamcoPblsalThingInqireSvc/getKamcoPblsalThingDtls"

def test_api():
    variations = [
        {"serviceKey": API_KEY, "cltrMngNo": "2026-0400-023211", "pageNo": 1, "numOfRows": 10},
        {"ServiceKey": API_KEY, "cltrMngNo": "20260400023211", "pageNo": 1, "numOfRows": 10},
        {"serviceKey": API_KEY, "cltrMngNo": "20260400023211"},
    ]
    
    for params in variations:
        try:
            print(f"Trying: {url} with params: {params}")
            # Use requests params which automatically url encodes keys/values
            response = requests.get(url, params=params, timeout=10)
            print("Status code:", response.status_code)
            print("Response:", response.text[:500])
        except Exception as e:
            print("Error:", e)
            
if __name__ == "__main__":
    test_api()
