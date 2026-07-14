import os

paths = [
    "c:/Users/llll/Documents/두인경매/바이브코딩/public/index.html",
    "c:/Users/llll/Documents/두인경매/바이브코딩/index.html"
]

for p in paths:
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        print(f"File: {p} ({len(content)} chars)")
        lines = content.split("\n")
        for idx, line in enumerate(lines):
            if "이슈" in line or "issues.html" in line:
                print(f"  L{idx+1}: {line.strip()[:120]}")
