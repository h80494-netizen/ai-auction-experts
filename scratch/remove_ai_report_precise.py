with open('public/analysis.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if '<!-- AI Overlap Report Section -->' in line:
        skip = True
    if '<!-- Complete list of matched auctions -->' in line:
        skip = False
    
    if '// Fetch AI Overlap Report using sorted case_nos and helper dicts' in line:
        skip = True
        
    if skip and '});' in line and 'document.getElementById(\'ai-report-content\').innerHTML' in lines[lines.index(line)-2] if lines.index(line) >= 2 else False:
        # this is the end of the fetch block:
        # 1080:             console.error(err);
        # 1081:             document.getElementById('ai-report-content').innerHTML = `<div style="color: #ef4444; padding: 10px;">⚠️ AI 분석 요청 중 오류가 발생했습니다.</div>`;
        # 1082:         });
        pass # Still skip this line
    elif skip and '    } else {' in line and lines[lines.index(line)+1].find('// No data') != -1:
        # This is line 1083. We should stop skipping here!
        skip = False
        new_lines.append(line)
        continue
        
    if not skip:
        # Also remove any leftover reference to ai-report-content
        if 'document.getElementById(\'ai-report-content\').innerHTML' not in line:
            new_lines.append(line)

with open('public/analysis.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Safely sliced out the exact sections.")
