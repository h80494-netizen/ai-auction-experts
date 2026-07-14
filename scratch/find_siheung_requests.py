with open('server.log', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print("All road_flows requests matching Siheung longitude (126.8 or 126.7):")
for idx, line in enumerate(lines):
    if 'road_flows' in line and ('126.8' in line or '126.7' in line or '126.80' in line):
        print(f"{idx+1}: {line.strip()}")
