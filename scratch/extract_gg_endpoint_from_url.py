import requests
from bs4 import BeautifulSoup
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://data.gg.go.kr/portal/data/service/selectServicePage.do"
params = {
    "infId": "S62GFEEN7JMLMA0PH6CF19108891",
    "infSeq": "1"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

try:
    print("Fetching page...")
    res = requests.get(url, params=params, headers=headers, verify=False)
    print("Status:", res.status_code)
    
    # Save raw html for debugging
    with open("scratch/service_page.html", "w", encoding="utf-8") as f:
        f.write(res.text)
        
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Look for openapi.gg.go.kr in text or attributes
    print("\nSearching for openapi URLs...")
    text_matches = re.findall(r"https://openapi\.gg\.go\.kr/[A-Za-z0-9_]+", res.text)
    print("Found direct matches:", set(text_matches))
    
    # Look for anything like /Gnrl or /Genl or /Refrm
    # Also find inputs, buttons, spans, or anything that might show the API name
    for tag in soup.find_all(True):
        for attr in ['value', 'data-id', 'id', 'class']:
            val = tag.get(attr, '')
            if isinstance(val, str) and ('api' in val.lower() or 'url' in val.lower()):
                print(f"Tag: {tag.name} | Attr: {attr}={val} | Text: {tag.get_text().strip()[:100]}")
                
except Exception as e:
    print("Error:", e)
