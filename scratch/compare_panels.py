with open('replace_panels.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's count how many times "toggle-gmr-pop-road" appears in replace_panels.py
count = content.count('toggle-gmr-pop-road')
print(f"Occurrences of 'toggle-gmr-pop-road' in replace_panels.py: {count}")
