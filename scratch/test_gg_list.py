import requests
from bs4 import BeautifulSoup
import json

def fetch_gg_list():
    url = "https://www.gg.go.kr/onnuri/list.do"
    print(f"Testing URL: {url}")
    res = requests.get(url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')

    print(f"Status Code: {res.status_code}")
    
    # Try to find list items or table rows
    items = []
    
    # Check for ul/li or table
    tables = soup.find_all('table')
    if tables:
        for tr in tables[0].find_all('tr')[1:5]:
            tds = tr.find_all('td')
            if tds:
                items.append([td.text.strip() for td in tds])
                
    lists = soup.find_all('ul', class_='list') or soup.find_all('ul', class_='board-list')
    if lists:
        for li in lists[0].find_all('li')[:5]:
            items.append(li.text.strip().replace('\n', ' '))
            
    with open("scratch/gg_list.json", "w", encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print("Saved items to gg_list.json")

if __name__ == "__main__":
    fetch_gg_list()
