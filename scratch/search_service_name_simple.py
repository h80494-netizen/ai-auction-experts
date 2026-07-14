with open("scratch/service_page.html", "r", encoding="utf-8") as f:
    html = f.read()

# Let's search for "openapi.gg.go.kr"
idx = 0
while True:
    pos = html.find("openapi.gg.go.kr", idx)
    if pos == -1:
        break
    # Print 200 chars around it
    print(f"\n--- Match at pos {pos} ---")
    print(html[pos-100:pos+200])
    idx = pos + 1

# Let's search for "/portal/openapi/"
idx = 0
while True:
    pos = html.find("/portal/openapi/", idx)
    if pos == -1:
        break
    print(f"\n--- Match portal openapi at pos {pos} ---")
    print(html[pos-50:pos+150])
    idx = pos + 1
