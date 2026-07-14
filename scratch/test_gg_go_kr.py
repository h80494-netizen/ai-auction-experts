import requests
from bs4 import BeautifulSoup

url = "https://www.gg.go.kr/onnuri/view.do?nowUrl=%2Fonnuri%2Fview.do%3Fno%3D109&no=109&sv=A&sc=%EC%9D%98%EC%99%95&sigunSeCd=&id=anyang&enfcMthdList=0001&enfcMthdList=0002&enfcMthdList=0003&enfcMthdList=0004&bizTypeList=0001&bizaraStepCdList=1100&bizaraStepCdList=1200&bizaraStepCdList=1300&bizaraStepCdList=1400&bizaraPrgrsStepCd=&sw=%EC%9D%B8%EB%8D%95%EC%9B%90"
print(f"Testing URL: {url}")
res = requests.get(url, verify=False)
soup = BeautifulSoup(res.text, 'html.parser')

print(f"Status Code: {res.status_code}")
print(f"Title: {soup.title.string if soup.title else 'No Title'}")
# Find a table or list
tables = soup.find_all('table')
if tables:
    for tr in tables[0].find_all('tr')[:5]:
        print([td.text.strip() for td in tr.find_all(['th', 'td'])])
else:
    print("No tables found. Printing body preview:")
    print(soup.body.text[:500].strip() if soup.body else "No Body")
