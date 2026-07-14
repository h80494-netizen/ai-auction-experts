from bs4 import BeautifulSoup

with open("scratch/search_result_stc_2.html", "r", encoding="utf-8") as f:
    h1 = f.read()

# Let's see if we have search_result_stc_2.html or any other saved file
import os
for f_name in os.listdir("scratch"):
    if f_name.endswith(".html"):
        with open(os.path.join("scratch", f_name), "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            title = soup.title.text.strip() if soup.title else "No Title"
            table = soup.select_one("table.tbl_auction_list")
            table_found = "Yes" if table else "No"
            print(f"File: {f_name} | Title: {title} | Table Found: {table_found} | Body Length: {len(soup.text)}")
