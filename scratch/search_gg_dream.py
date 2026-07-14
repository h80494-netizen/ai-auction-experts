import requests
import json

url = "https://data.gg.go.kr/portal/dataset/search.do"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
params = {
    "searchText": "일반 정비 사업 추진 현황",
    "page": 1,
    "rows": 10
}

try:
    response = requests.get(url, headers=headers, params=params, verify=False)
    print("Status Code:", response.status_code)
    # print first 1000 characters
    print(response.text[:1000])
    
    # Try parsing json
    try:
        data = response.json()
        print("Keys:", data.keys())
        if 'list' in data:
            for item in data['list']:
                print(f"Name: {item.get('title')} | infId: {item.get('infId')} | infSeq: {item.get('infSeq')}")
    except Exception as e:
        print("JSON Parse error:", e)
except Exception as e:
    print("Request failed:", e)
