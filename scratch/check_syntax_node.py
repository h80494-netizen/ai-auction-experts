import re
import subprocess

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
if not match:
    print("No script block found")
    sys.exit(1)

script = match.group(1)

# Write to temp.js
with open('scratch/temp_map.js', 'w', encoding='utf-8') as f:
    f.write(script)

print("Running node --check on the script...")
res = subprocess.run(['node', '--check', 'scratch/temp_map.js'], capture_output=True, text=True)
if res.returncode == 0:
    print("SUCCESS! No JS syntax errors found by node!")
else:
    print("ERROR! Node found syntax errors:")
    print(res.stderr)
