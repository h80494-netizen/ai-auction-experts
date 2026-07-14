with open('public/map.html', 'r', encoding='cp949', errors='replace') as f:
    lines = f.readlines()

print("Line 1740-1750:")
for i in range(1740, 1750):
    print(f"{i}: {lines[i-1].strip()}")

print("\nLine 2050-2060:")
for i in range(2050, 2060):
    print(f"{i}: {lines[i-1].strip()}")
