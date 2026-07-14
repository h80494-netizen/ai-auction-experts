import re

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the script block
match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
if not match:
    print("No script block found")
    sys.exit(1)

script = match.group(1)
lines = script.split('\n')

balance = 0
for idx, line in enumerate(lines):
    # Remove strings to avoid counting parentheses in strings
    # Simple regex to remove string literals
    clean_line = re.sub(r'".*?"|\'.*?\'|`.*?`', '', line)
    
    # We also ignore comments
    if '//' in clean_line:
        clean_line = clean_line.split('//')[0]
        
    for char in clean_line:
        if char == '(':
            balance += 1
        elif char == ')':
            balance -= 1
            if balance < 0:
                print(f"Parenthesis balance went below zero at line {idx+1}: {line}")
                balance = 0

print("Final balance:", balance)
