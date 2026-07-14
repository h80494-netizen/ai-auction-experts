with open('backend/ai_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
fn_match = re.search(r'def analyze_overlap_cases.*?(?=\ndef|$)', content, re.DOTALL)
if fn_match:
    with open('scratch/search_ai.txt', 'w', encoding='utf-8') as out:
        out.write(fn_match.group(0))
    print("Success")
else:
    print("Not found")
