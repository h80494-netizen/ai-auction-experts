with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("toggle-old-buildings count:", content.count("toggle-old-buildings"))
print("layers.oldBuildings count:", content.count("layers.oldBuildings"))
