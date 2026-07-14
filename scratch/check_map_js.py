import re

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract all script blocks
scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
print(f"Number of script blocks found: {len(scripts)}")

# Try to compile each script block (using python js syntax checker or simple inspection)
# Since we don't have JS compiler, we can check basic braces/parentheses balances!
for idx, script in enumerate(scripts):
    print(f"Block {idx+1} length: {len(script)}")
    # Count braces
    open_braces = script.count('{')
    close_braces = script.count('}')
    open_parens = script.count('(')
    close_parens = script.count(')')
    print(f"  Braces: {{ = {open_braces}, }} = {close_braces}")
    print(f"  Parens: ( = {open_parens}, ) = {close_parens}")
    if open_braces != close_braces:
        print("  WARNING: BRACE MISMATCH!")
    if open_parens != close_parens:
        print("  WARNING: PARENTHESIS MISMATCH!")
