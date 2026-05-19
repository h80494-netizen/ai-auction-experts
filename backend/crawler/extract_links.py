from bs4 import BeautifulSoup
import json

with open("detail_table.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
links = []
for a in soup.find_all('a'):
    links.append({'text': a.text.strip(), 'href': a.get('href', '')})

with open("links.json", "w", encoding="utf-8") as f:
    json.dump(links, f, ensure_ascii=False, indent=2)
print("Extracted links")
