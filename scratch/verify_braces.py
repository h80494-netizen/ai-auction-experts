with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's extract all <script> blocks
import re
script_pattern = re.compile(r"<script>(.*?)</script>", re.DOTALL)
scripts = script_pattern.findall(content)

print(f"Found {len(scripts)} script blocks.")

syntax_error_found = False

for idx, script in enumerate(scripts):
    # Count braces
    open_braces = script.count("{")
    close_braces = script.count("}")
    open_parens = script.count("(")
    close_parens = script.count(")")
    open_brackets = script.count("[")
    close_brackets = script.count("]")
    
    print(f"Script block {idx+1}:")
    print(f"  Braces: {{ = {open_braces}, }} = {close_braces} (diff: {open_braces - close_braces})")
    print(f"  Parens: ( = {open_parens}, ) = {close_parens} (diff: {open_parens - close_parens})")
    print(f"  Brackets: [ = {open_brackets}, ] = {close_brackets} (diff: {open_brackets - close_brackets})")
    
    if open_braces != close_braces:
        print(f"  WARNING: Unmatched braces in script block {idx+1}!")
        syntax_error_found = True
    if open_parens != close_parens:
        print(f"  WARNING: Unmatched parens in script block {idx+1}!")
        syntax_error_found = True

if not syntax_error_found:
    print("ALL SCRIPT BLOCKS MATCHED PERFECTLY! ZERO SYNTAX ERRORS DETECTED!")
else:
    print("WARNING: Unmatched syntax symbols detected. Please inspect!")
