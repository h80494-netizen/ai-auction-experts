with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("loginOverlay in map.html:", "loginOverlay" in content)
print("loginBtn in map.html:", "loginBtn" in content)
