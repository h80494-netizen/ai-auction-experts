from bs4 import BeautifulSoup

with open("scratch/search_result_6060.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
table = soup.select_one("table.tbl_auction_list")

if table:
    print("--- tbl_auction_list table found ---")
    rows = table.find_all('tr')
    print(f"Total rows: {len(rows)}")
    for i, row in enumerate(rows):
        print(f"Row {i}: {row.text.strip().replace('\n', ' ')[:200]}")
else:
    print("Table 'table.tbl_auction_list' not found in HTML!")
    # Let's see what tables exist
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables on the page:")
    for idx, t in enumerate(tables):
        print(f"Table {idx}: class={t.get('class')} | id={t.get('id')}")
