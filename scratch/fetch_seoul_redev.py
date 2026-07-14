import requests
from bs4 import BeautifulSoup
import json

def fetch_map_status():
    res = requests.post("https://cleanup.seoul.go.kr/cleanup/bsnssttus/selectBsnsSttusList.do", data={
        "pageIndex": 1,
        "searchGu": "",
        "searchDong": "",
        "searchBsnsSe": "",
        "searchSttus": "",
        "searchNm": ""
    })
    print("Status code:", res.status_code)
    try:
        data = res.json()
        print(f"Total count: {data.get('totCnt')}")
        for item in data.get('list', [])[:5]:
            print(f"{item.get('BSNS_NM', '')}: {item.get('PROGRS_STTUS_NM', '')} ({item.get('GU_NM')} {item.get('DONG_NM')})")
    except Exception as e:
        print("Error parsing JSON:", e)
        # If not JSON, maybe HTML
        print(res.text[:1000].encode('utf-8', 'ignore').decode('utf-8'))

if __name__ == "__main__":
    fetch_map_status()
