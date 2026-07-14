import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

inf_id = "S62GFEEN7JMLMA0PH6CF19108891"

# Guess some common metadata URL endpoints on Gyeonggi portal
endpoints = [
    "https://data.gg.go.kr/portal/data/service/selectServiceInfo.do",
    "https://data.gg.go.kr/portal/data/service/selectMetaInfo.do",
    "https://data.gg.go.kr/portal/data/service/selectApiInfo.do",
    "https://data.gg.go.kr/portal/data/service/selectOpenApiInfo.do",
    "https://data.gg.go.kr/portal/data/service/selectTblColList.do"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": f"https://data.gg.go.kr/portal/data/service/selectServicePage.do?infId={inf_id}&infSeq=1"
}

for ep in endpoints:
    try:
        print(f"\nTrying endpoint: {ep}")
        res = requests.post(ep, data={"infId": inf_id, "infSeq": "1"}, headers=headers, verify=False)
        print("Status:", res.status_code)
        print("Response Length:", len(res.text))
        if res.status_code == 200 and len(res.text) > 10:
            print("Response Sample:")
            print(res.text[:2000])
            with open(f"scratch/{ep.split('/')[-1].replace('.do', '.json')}", "w", encoding="utf-8") as f:
                f.write(res.text)
    except Exception as e:
        print("Error:", e)
