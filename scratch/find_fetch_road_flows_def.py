with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
for idx, line in enumerate(lines):
    if 'function fetchRoadFlows' in line or 'fetchRoadFlows = ' in line:
        print(f"Line {idx+1}: {line}")
        # print 75 lines
        for j in range(idx, min(len(lines), idx+75)):
            print(f"  {j+1}: {lines[j]}")
