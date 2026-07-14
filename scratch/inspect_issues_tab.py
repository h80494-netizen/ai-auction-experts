import os

file_path = "c:/Users/llll/Documents/두인경매/바이브코딩/public/issues.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace "재개발" with "재개발재건축" for the tab button and category logic if needed.
# But wait, if the DB category is "재개발", we should keep data-category="재개발" and just change the display text.
# Let's see what the current tab looks like.

lines = content.split('\n')
for i, line in enumerate(lines):
    if 'data-category="재개발"' in line:
        print(f"Line {i+1}: {line}")
    elif 'onclick="selectTabCategory(\'재개발\')"' in line:
        print(f"Line {i+1}: {line}")

