with open("backend/crawler/myauction_scraper.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Searching for lease/tenant parsing in myauction_scraper.py:")
for idx, line in enumerate(lines):
    if "임차" in line or "tenant" in line or "lease" in line or "보증금" in line or "월세" in line or "미상" in line:
        print(f"{idx+1}: {line.strip()}")
