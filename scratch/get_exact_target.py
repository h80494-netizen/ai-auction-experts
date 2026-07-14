with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
# lines are 0-indexed, so 1703 is index 1702, 1894 is index 1893
target_lines = lines[1702:1894]
target_str = '\n'.join(target_lines)

# Write this to a temp file in scratch directory so we can read it easily
with open('scratch/exact_target_str.txt', 'w', encoding='utf-8') as out:
    out.write(target_str)

print("Exact target string length:", len(target_str))
