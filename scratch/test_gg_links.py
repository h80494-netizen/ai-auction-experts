import requests
from bs4 import BeautifulSoup
import json

url = "https://www.gg.go.kr/onnuri/view.do?nowUrl=%2Fonnuri%2Fview.do%3Fno%3D109&no=109&sv=A&sc=%EC%9D%98%EC%99%95&sigunSeCd=&id=anyang&enfcMthdList=0001&enfcMthdList=0002&enfcMthdList=0003&enfcMthdList=0004&bizTypeList=0001&bizaraStepCdList=1100&bizaraStepCdList=1200&bizaraStepCdList=1300&bizaraStepCdList=1400&bizaraPrgrsStepCd=&sw=%EC%9D%B8%EB%8D%95%EC%9B%90"
res = requests.get(url, verify=False)
soup = BeautifulSoup(res.text, 'html.parser')

links = []
for a in soup.find_all('a', href=True):
    links.append(a['href'])
    
with open("scratch/gg_links.json", "w", encoding='utf-8') as f:
    json.dump(links, f, ensure_ascii=False, indent=2)
print(f"Saved {len(links)} links to gg_links.json")
