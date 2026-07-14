import re

path = "scratch/service_page.html"

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# Let's search for case-insensitive Gnrl or Genl or Maint or Biz or Promt or Stat or Sttus
patterns = [
    r"[a-zA-Z]*maint[a-zA-Z]*",
    r"[a-zA-Z]*gnrl[a-zA-Z]*",
    r"[a-zA-Z]*refrm[a-zA-Z]*",
    r"[a-zA-Z]*promt[a-zA-Z]*",
    r"[a-zA-Z]*sttus[a-zA-Z]*",
    r"openapi\.gg\.go\.kr/[a-zA-Z]+"
]

print("Matches:")
for pat in patterns:
    matches = re.findall(pat, html, re.IGNORECASE)
    if matches:
        print(f"Pattern '{pat}':", set(matches))
