import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/modify_map_stages.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find all variable assignments of triple-quoted strings
import re
vars_found = re.findall(r'(\w+)\s*=\s*"""(.*?)"""', content, re.DOTALL)
print(f"Found {len(vars_found)} variables with triple-quoted strings:")
for name, val in vars_found:
    print(f"Variable name: '{name}', value length: {len(val)}")
    # If it contains HTML toggles, print it
    if 'id=' in val or 'class=' in val or 'toggle-' in val:
        print(f"  Snippet:\n{val[:1000]}\n  ...")
