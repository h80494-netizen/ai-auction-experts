import re

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find the start of left panel <!-- Left Panel: Layer List -->
start_idx = content.find('<!-- Left Panel: Layer List -->')
if start_idx == -1:
    print("Left Panel comment NOT found!")
else:
    # Print the next 2000 characters
    print("Left Panel Content:")
    print(content[start_idx:start_idx+2000])
