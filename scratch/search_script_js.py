with open('public/script.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'loginOverlay' in line or 'password' in line or 'passwordInput' in line:
        print(f"Line {idx+1}: {line.strip()}")
