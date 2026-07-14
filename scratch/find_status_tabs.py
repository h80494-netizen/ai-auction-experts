with open("scratch/search_result_6060.html", "r", encoding="utf-8") as f:
    content = f.read()

# Let's search for keywords in Korean
keywords = ["진행물건", "예정물건", "결과물건", "종결물건", "매각결과", "전체물건", "spels", "pchs", "schs"]
print("--- Text Matches in search_result_6060.html ---")
for kw in keywords:
    count = content.count(kw)
    print(f"Keyword '{kw}': {count} occurrences")

# Find all links on the page and see if there are any that change pchs/schs
import re
links = re.findall(r'href=["\']([^"\']+)["\']', content)
print("\n--- Links with different state parameters ---")
found_diff = False
for link in links:
    if 'spels=' in link or 'pchs=' in link or 'schs=' in link:
        if 'spels=Y&schs=N&pchs=N' not in link:
            print(link)
            found_diff = True
if not found_diff:
    print("None found, all state-changing links have spels=Y&schs=N&pchs=N")
