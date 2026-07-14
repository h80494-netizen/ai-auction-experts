with open('backend/ai_analyzer.py', 'rb') as f:
    data = f.read()

print("Bytes around 13189:")
start = max(0, 13180)
end = min(len(data), 13220)
chunk = data[start:end]
print(chunk)
for idx, b in enumerate(chunk):
    print(f"{start + idx}: {hex(b)} ({chr(b) if 32 <= b < 127 else '?'})")
