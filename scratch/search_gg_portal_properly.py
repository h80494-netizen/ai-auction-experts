import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Let's search using the public portal search page
url = "https://data.gg.go.kr/portal/dataset/search.do"
params = {
    "searchText": "일반 정비 사업 추진 현황"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

try:
    # First, let's try searching on the HTML search page
    search_url = "https://data.gg.go.kr/portal/dataset/search.do"
    res = requests.get(search_url, params=params, headers=headers, verify=False)
    print("Status:", res.status_code)
    
    soup = BeautifulSoup(res.text, 'html.parser')
    # Find all links
    links = soup.find_all('a')
    print(f"Found {len(links)} links on the page.")
    for link in links:
        href = link.get('href', '')
        text = link.get_text().strip()
        if '정비' in text or '재개발' in text or 'selectServicePage' in href:
            print(f"Link Text: {text} | Href: {href}")
            
except Exception as e:
    print("Error:", e)
