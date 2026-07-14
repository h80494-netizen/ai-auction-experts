from bs4 import BeautifulSoup

with open("scratch/search_result_6060.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
aresult_select = soup.find('select', attrs={'name': 'aresult'})
if aresult_select:
    print("--- aresult select options ---")
    for opt in aresult_select.find_all('option'):
        val = opt.get('value', '')
        text = opt.text.strip()
        print(f"Value: {val} | Text: {text}")
else:
    print("Select aresult not found")
