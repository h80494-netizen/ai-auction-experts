from bs4 import BeautifulSoup

with open("error_dump.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
print("Title of page:", soup.title.text if soup.title else "No title")

# Print all tables and their rows count
tables = soup.find_all("table")
print(f"Found {len(tables)} tables.")
for idx, tbl in enumerate(tables):
    rows = tbl.find_all("tr")
    print(f" - Table {idx}: class={tbl.get('class')}, rows={len(rows)}")

# Print links matching view or containing digits
links = soup.find_all("a")
print(f"Found {len(links)} links.")
for l in links[:50]:
    href = l.get("href")
    text = l.text.strip().replace("\n", "")
    if href:
        print(f" - Link: text='{text}', href='{href}'")
