import urllib.parse
from bs4 import BeautifulSoup

with open("scratch/search_result_6060.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("--- Sub-tabs / Link Filters on search page ---")
for a in soup.find_all('a', href=True):
    href = a['href']
    if 'search_list.php' in href or 'search.php' in href:
        parsed_url = urllib.parse.urlparse(href)
        params = urllib.parse.parse_qs(parsed_url.query)
        # Only show unique filter changes
        filtered_params = {k: v for k, v in params.items() if k in ['spels', 'schs', 'pchs', 'npls', 'aresult']}
        if filtered_params or a.text.strip():
            print(f"Text: {a.text.strip()} | URL: {href} | Relevant Params: {filtered_params}")
