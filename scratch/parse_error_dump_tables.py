from bs4 import BeautifulSoup

with open("error_dump.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
table = soup.find("table", class_="tbl_auction_list")
if table:
    print("Found tbl_auction_list.")
    rows = table.find_all("tr")
    for idx, r in enumerate(rows):
        cells = r.find_all(["td", "th"])
        cell_texts = [c.text.strip().replace("\n", " ") for c in cells]
        print(f"Row {idx}: {cell_texts}")
else:
    print("tbl_auction_list not found.")
