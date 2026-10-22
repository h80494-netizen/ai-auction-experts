import re

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove toggle-dev2 from toggleMap
content = re.sub(r"\s*'toggle-dev2':\s*\[layers\.dev2\],", "", content)

# 2. Add safeguard to toggleMap forEach
old_toggle_loop = """            Object.keys(toggleMap).forEach(id => {
                document.getElementById(id).addEventListener('change', (e) => {"""
new_toggle_loop = """            Object.keys(toggleMap).forEach(id => {
                const el = document.getElementById(id);
                if (!el) return;
                el.addEventListener('change', (e) => {"""
content = content.replace(old_toggle_loop, new_toggle_loop)

# 3. Remove toggle-dev2 from allToggles in updateHighlighterPanel
content = re.sub(r"\s*\{\s*id:\s*'toggle-dev2'.*?\},", "", content)

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed toggle-dev2 references causing crash.")
