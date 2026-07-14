import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

inf_id = "S62GFEEN7JMLMA0PH6CF19108891"

# Guess some common download URLs
download_urls = [
    f"https://data.gg.go.kr/portal/data/service/download.do?infId={inf_id}&infSeq=1&fileType=CSV",
    f"https://data.gg.go.kr/portal/data/service/fileDownload.do?infId={inf_id}&infSeq=1&fileType=CSV",
    f"https://data.gg.go.kr/portal/data/service/downloadCSV.do?infId={inf_id}&infSeq=1",
    f"https://data.gg.go.kr/portal/data/service/fileDownload.do?infId={inf_id}&infSeq=1"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": f"https://data.gg.go.kr/portal/data/service/selectServicePage.do?infId={inf_id}&infSeq=1"
}

for url in download_urls:
    try:
        print(f"\nTrying download URL: {url}")
        res = requests.get(url, headers=headers, verify=False, timeout=10)
        print("Status:", res.status_code)
        print("Response Length:", len(res.text))
        print("Content-Type:", res.headers.get("Content-Type", ""))
        
        # Check if response is CSV (typically starts with header columns like 시군명 or similar)
        # or check if it starts with dynamic file markers
        if res.status_code == 200 and "text/html" not in res.headers.get("Content-Type", ""):
            print("Successfully downloaded! Sample:")
            # Try decoding in cp949 or utf-8
            for enc in ['cp949', 'utf-8', 'euc-kr']:
                try:
                    text = res.content.decode(enc)
                    print(text[:300])
                    # Save to data folder
                    with open(r"c:\Users\llll\Documents\두인경매\바이브코딩\data\경기재개발추진현황.csv", "w", encoding="utf-8") as f:
                        f.write(text)
                    print("Saved Gyeonggi CSV to data/경기재개발추진현황.csv")
                    break
                except Exception as e:
                    pass
            break
    except Exception as e:
        print("Error:", e)
