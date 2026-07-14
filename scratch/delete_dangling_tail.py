with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Deleting lines...")
del lines[2242:2247]

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Successfully deleted lines and saved map.html")
