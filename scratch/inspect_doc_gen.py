with open('backend/doc_generator.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print(f"File size: {len(content)} characters")

# Find any functions or classes
import re
functions = re.findall(r'def\s+(\w+)\(', content)
print("Functions in doc_generator.py:", functions)

# Search for any file paths or HTML-related strings
for idx, line in enumerate(content.split('\n')):
    if any(k in line.lower() for k in ['html', 'template', 'open', 'write', 'save', 'file']):
        print(f"Line {idx+1}: {line.strip()[:120]}")
