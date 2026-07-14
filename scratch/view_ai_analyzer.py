with open('backend/ai_analyzer.py', 'rb') as f:
    data = f.read()

text = data.decode('utf-8', errors='replace')
lines = text.split('\n')
with open('scratch/ai_analyzer_lines.txt', 'w', encoding='utf-8') as out:
    for idx in range(235, min(350, len(lines))):
        out.write(f"{idx+1}: {lines[idx]}\n")

print("Wrote lines to scratch/ai_analyzer_lines.txt")
