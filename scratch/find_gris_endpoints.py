import requests
import re
from bs4 import BeautifulSoup

url = "https://gris.gg.go.kr/map/main/grisMapView.do"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36'
}

try:
    print("Fetching grisMapView.do...")
    res = requests.get(url, headers=headers, verify=False, timeout=15)
    print("Status:", res.status_code)
    
    # Save HTML to scratch for reference
    with open("scratch/grisMapView.html", "w", encoding="utf-8") as f:
        f.write(res.text)
    print("Saved HTML to scratch/grisMapView.html")
    
    # Search for all script tags
    soup = BeautifulSoup(res.text, 'html.parser')
    scripts = soup.find_all('script')
    print(f"Found {len(scripts)} script tags.")
    
    # Search for AJAX endpoints or URLs
    endpoints = set()
    for s in scripts:
        if s.get('src'):
            src = s.get('src')
            if not src.startswith("http"):
                src = "https://gris.gg.go.kr" + (src if src.startswith("/") else "/" + src)
            endpoints.add(src)
        else:
            # Inline script parsing
            text = s.string or ""
            # Find anything like /dev/...do or /map/...do or /gis/...do
            found = re.findall(r'[\'"](/[a-zA-Z0-9_\-/]+\.do)[\'"]', text)
            for f in found:
                print("Found inline endpoint:", f)
                
    # Fetch some script contents and scan them
    for src in list(endpoints)[:10]:
        print(f"\nScanning script: {src}")
        try:
            js_res = requests.get(src, headers=headers, verify=False, timeout=5)
            # Find URLs in JavaScript
            urls = re.findall(r'[\'"](/[a-zA-Z0-9_\-/]+\.do)[\'"]', js_res.text)
            for u in set(urls):
                print("Found JS endpoint:", u)
        except Exception as jse:
            print("Failed to fetch JS:", jse)
            
except Exception as e:
    print("Error:", e)
