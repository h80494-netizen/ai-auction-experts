import os

for root, dirs, files in os.walk('.'):
    if '.git' in root or 'node_modules' in root or '.system_generated' in root:
        continue
    for file in files:
        if file.endswith(('.html', '.js', '.py', '.txt', '.bat', '.sh')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if 'overpass' in content.lower():
                    print(f"Found in {path}")
            except Exception:
                pass
