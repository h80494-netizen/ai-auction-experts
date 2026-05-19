import requests

url = "https://www.onbid.co.kr/op/meminf/lgnmng/prtllgn/PrtlLgnController/main.do"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
print("Status Code:", response.status_code)

html = response.text
with open("onbid_requests.html", "w", encoding="utf-8") as f:
    f.write(html)
    
print("Saved to onbid_requests.html")
print(html[:500])
