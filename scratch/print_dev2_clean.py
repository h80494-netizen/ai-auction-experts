with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('scratch/dev2_clean.txt', 'w', encoding='utf-8') as out:
    for idx, line in enumerate(lines):
        if 'layers.dev2' in line or 'fetchDistrictUnits' in line:
            out.write(f"=== Match at line {idx+1} ===\n")
            for i in range(max(0, idx - 5), min(len(lines), idx + 8)):
                out.write(f'  {i+1}: {lines[i]}')
            out.write("\n")

print("SUCCESS: Written to scratch/dev2_clean.txt")
