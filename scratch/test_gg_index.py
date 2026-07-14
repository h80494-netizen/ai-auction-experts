import requests
from bs4 import BeautifulSoup
import re

url = "https://www.gg.go.kr/onnuri/index.do"
res = requests.get(url, verify=False)
soup = BeautifulSoup(res.text, 'html.parser')

scripts = soup.find_all('script')
ajax_urls = set()
for script in scripts:
    if script.string:
        urls = re.findall(r'[\'"](/onnuri/[^\'"]+\.do)[^\'"]*[\'"]', script.string)
        ajax_urls.update(urls)

print("Ajax/Action URLs found:")
for u in ajax_urls:
    print(u)
    
# also check inline scripts
with open('scratch/gg_index.html', 'w', encoding='utf-8') as f:
    f.write(res.text)
