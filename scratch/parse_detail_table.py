import os
from bs4 import BeautifulSoup

path = r"backend/detail_table.html"
if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    print(f"Total tables: {len(tables)}")
    with open("scratch/table_output.txt", "w", encoding="utf-8") as out:
        for idx, table in enumerate(tables):
            text = table.get_text()
            if "임차인" in text and "전입일자" in text and "보증금" in text:
                out.write(f"=== Tenant Table Found at Index {idx} ===\n")
                trs = table.find_all("tr")
                for r_idx, tr in enumerate(trs):
                    tds = tr.find_all(["td", "th"])
                    tds_info = []
                    for c_idx, td in enumerate(tds):
                        colspan = td.get("colspan", "1")
                        text_val = " ".join(td.get_text().split())
                        tds_info.append(f"Cell {c_idx} (colspan={colspan}): {text_val}")
                    out.write(f"Row {r_idx}: " + " | ".join(tds_info) + "\n")
                out.write("=" * 50 + "\n")
else:
    print("detail_table.html not found")
