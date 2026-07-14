import requests
import json

url = "https://www.gg.go.kr/onnuri/mbiz/boss/info/biz/ajaxGetBizaraList.do"
headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.gg.go.kr",
    "Referer": "https://www.gg.go.kr/onnuri/index.do"
}
payload = {
    "pageIndex": "1",
    "recordCountPerPage": "100"
}
try:
    res = requests.post(url, headers=headers, data=payload, verify=False)
    data = res.json()
    print(f"Total entries: {data.get('paginationInfo', {}).get('totalRecordCount')}")
    if 'list' in data:
        for item in data['list'][:5]:
            print(f"{item.get('sigunSeNm')} {item.get('bizaraNm')} - {item.get('bizaraPrgrsStepNm')} ({item.get('bizaraStepNm')})")
    with open("scratch/gg_ajax.json", "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
except Exception as e:
    print(f"Error: {e}")
    if 'res' in locals():
        print(res.status_code)
        print(res.text[:500])
