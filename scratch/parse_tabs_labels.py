import re
from bs4 import BeautifulSoup

with open("scratch/search_result_6060.html", "r", encoding="utf-8") as f:
    html = f.read()

# Let's search for tags like ul with class "tab" or similar
soup = BeautifulSoup(html, 'html.parser')

print("--- Searching for tabs or list items ---")
for ul in soup.find_all('ul'):
    ul_text = ul.text.strip().replace('\n', ' ')
    if '진행' in ul_text or '결과' in ul_text or '예정' in ul_text or '종결' in ul_text or 'spels' in str(ul):
        print(f"UL class={ul.get('class')}:")
        for li in ul.find_all('a'):
            print(f"  Link Text: {li.text.strip()} | Href: {li.get('href')}")

# Also check any links with spels/pchs/schs in general
print("\n--- Any links with spels/pchs/schs ---")
for a in soup.find_all('a', href=True):
    href = a['href']
    if any(param in href for param in ['spels', 'pchs', 'schs']):
        print(f"  Link Text: {a.text.strip()} | Href: {href}")
