with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for "@app.get" or "@app.post"
lines = content.split('\n')
for i, line in enumerate(lines):
    if "@app.get(" in line or "@app.post(" in line:
        print(f"   Line {i+1}: {line.strip()[:140]}")
