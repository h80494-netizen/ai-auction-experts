with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_script = False
script_lines = []
for idx, line in enumerate(lines):
    line_num = idx + 1
    if '<script>' in line:
        in_script = True
        continue
    if '</script>' in line:
        in_script = False
        continue
    if in_script:
        script_lines.append((line_num, line))

stack = []
in_string = None
in_line_comment = False
in_block_comment = False

for line_num, line in script_lines:
    i = 0
    n = len(line)
    while i < n:
        char = line[i]
        if in_block_comment:
            if char == '*' and i + 1 < n and line[i+1] == '/':
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue
        if in_line_comment:
            break
        if in_string:
            if char == '\\':
                i += 2
                continue
            if char == in_string:
                in_string = None
                i += 1
                continue
            i += 1
            continue
        if char == '/' and i + 1 < n and line[i+1] == '/':
            in_line_comment = True
            break
        if char == '/' and i + 1 < n and line[i+1] == '*':
            in_block_comment = True
            i += 2
            continue
        if char in ['"', "'", '`']:
            in_string = char
            i += 1
            continue
        if char == '{':
            stack.append((line_num, i, '{'))
        elif char == '}':
            if not stack:
                print(f"Extra closing brace '}}' at line {line_num}, col {i}")
            else:
                stack.pop()
        i += 1
    in_line_comment = False

if stack:
    print("Unmatched opening braces:")
    # print first 10 and last 10
    if len(stack) <= 20:
        for l_num, col, _ in stack:
            print(f"  Line {l_num}, col {col}")
    else:
        for l_num, col, _ in stack[:10]:
            print(f"  Line {l_num}, col {col}")
        print("  ...")
        for l_num, col, _ in stack[-10:]:
            print(f"  Line {l_num}, col {col}")
else:
    print("No unmatched braces!")
