import re

path = "scratch/service_page.html"

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# Let's search for javascript functions or ajax urls (.do)
matches = re.findall(r"/[a-zA-Z0-9_/]+\.do", html)
print("Found .do URLs:")
for m in set(matches):
    if 'service' in m or 'api' in m or 'select' in m or 'get' in m:
        print("  ", m)

# Let's print any script blocks containing 'infId'
scripts = re.findall(r"<script.*?>([\s\S]*?)</script>", html)
print(f"\nFound {len(scripts)} script blocks.")
for idx, script in enumerate(scripts):
    if 'infId' in script:
        print(f"\n--- Script {idx} containing 'infId' (first 1000 chars) ---")
        print(script.strip()[:1000])
