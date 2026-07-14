import re
from bs4 import BeautifulSoup

with open("scratch/search_result_6060.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("--- spels, schs, pchs inputs ---")
for name in ['spels', 'schs', 'pchs', 'npls']:
    inputs = soup.find_all('input', attrs={'name': name})
    for inp in inputs:
        print(f"Input: name={inp.get('name')}, type={inp.get('type')}, value={inp.get('value')}")

# Let's search the HTML content for these terms to see where they are referenced or toggled by checkboxes/scripts
for term in ['spels', 'schs', 'pchs', 'npls']:
    matches = [line.strip() for line in html.splitlines() if term in line]
    print(f"\nReferences to {term}:")
    for m in matches[:5]:
        print(m[:120])
