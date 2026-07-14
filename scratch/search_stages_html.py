import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/modify_map_stages.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = re.findall(r'new_html\s*=\s*"""(.*?)"""', content, re.DOTALL)
with open('scratch/stages_html.txt', 'w', encoding='utf-8') as out:
    for i, m in enumerate(matches):
        out.write(f"\n=========================================\n")
        out.write(f"MATCH {i+1}\n")
        out.write(f"=========================================\n")
        out.write(m)
        out.write("\n")

print("Done! Saved to scratch/stages_html.txt")
