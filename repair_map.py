import os

js_code = ''
with open('fix_js.py', 'r', encoding='utf-8') as f:
    text = f.read()
    js_code = text.split("js_code = r'''")[1].split("'''")[0]

content = open('public/map.html', encoding='utf-8').read()

if js_code in content:
    content = content.replace(js_code + '\n', '')
elif js_code.strip() in content:
    content = content.replace(js_code.strip(), '')

# remove the broken powershell injection as well
if '// --- GIS 고도화 기능 ---' in content:
    idx = content.find('// --- GIS 고도화 기능 ---')
    if content.rfind('</script>', 0, idx) == -1: # Meaning it's at the top
        pass # we handled it above

# Just remove ALL instances of JS code
while '// --- GIS 고도화 기능 ---' in content:
    start_idx = content.find('// --- GIS 고도화 기능 ---')
    # Find the end of this injected block, which ends with "    }\n}"
    end_text = "    }\n}"
    end_idx = content.find(end_text, start_idx) + len(end_text)
    if end_idx < len(end_text): break
    
    # Actually wait, let's just use string split if we can find the exact bounds
    # For safety, since it could be corrupted, I will just cut from start_idx to the next </script> or end of corrupted part
    
    # The powershell injection might be corrupted, so I will cut until the next function or </script>
    content = content[:start_idx] + content[end_idx:]

last_script_pos = content.rfind('</script>')
if last_script_pos != -1:
    content = content[:last_script_pos] + js_code + '\n' + content[last_script_pos:]

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Repaired')
