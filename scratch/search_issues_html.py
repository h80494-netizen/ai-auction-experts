with open('public/issues.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'function triggerRadarScan' in line or 'triggerRadarScan =' in line:
        print(f"Line {idx+1}: {line.strip()}")
        for j in range(max(0, idx-5), min(len(lines), idx+45)):
            print(f"  {j+1}: {lines[j].rstrip()}")
        print("-" * 50)
