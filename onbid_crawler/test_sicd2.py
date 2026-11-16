import requests
from bs4 import BeautifulSoup

response = requests.get('https://www.dooinauction.com/ca/caList.php', headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(response.text, 'html.parser')
select = soup.find('select', {'id': 'siCd'})
if select:
    for opt in select.find_all('option'):
        print(f"{opt.text.strip()}:{opt.get('value')}")
