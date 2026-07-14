import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/case_detail_dump.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print("=== Checking status keywords in elements ===")
keywords = ["진행", "낙찰", "유찰", "변경", "취소", "취하", "정지", "종결"]
for tag in soup.find_all(True):
    # Only check tags that don't have child elements to avoid duplicates
    if not any(child.name for child in tag.children):
        text = tag.get_text().strip()
        if any(kw in text for kw in keywords):
            print(f"<{tag.name} class='{tag.get('class', '')}' id='{tag.get('id', '')}'>: {text}")
