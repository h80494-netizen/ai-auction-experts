from bs4 import BeautifulSoup
import sys

try:
    with open('public/map.html', 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all('script')
    
    with open('temp_script_check.js', 'w', encoding='utf-8') as f:
        for i, script in enumerate(scripts):
            if script.string:
                f.write(f"\n// Script block {i}\n")
                f.write(script.string)
    print("Extracted scripts successfully.")
except Exception as e:
    print(f"Error: {e}")
