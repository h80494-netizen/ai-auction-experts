import re

path = "scratch/service_page.html"

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# Let's search for openapi in case-insensitive
matches = re.findall(r"openapi[^\s'\"]*", html, re.IGNORECASE)
print("Openapi occurrences:", set(matches))

# Let's search for any English identifiers in the page that look like Gyeonggi service names (usually capitalized, e.g. Gnrl...)
# Let's search for uppercase words with at least 8 letters
words = re.findall(r"\b[A-Za-z0-9_]{8,50}\b", html)
print("\nUnique english words in HTML (length >= 8, sample):")
# Filter some boring ones
boring = {'javascript', 'stylesheet', 'jquery', 'bootstrap', 'document', 'function', 'window', 'typeof', 'undefined'}
filtered = {w for w in words if w.lower() not in boring and not w.isdigit()}
print(sorted(list(filtered))[:100])
