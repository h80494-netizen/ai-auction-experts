with open("backend/server.log", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print(f"Total log lines: {len(lines)}")
print("Last 30 lines of backend/server.log:")
for l in lines[-30:]:
    print(l.strip())

print("\nSearching for road flow fetch logs in server.log:")
road_logs = [l.strip() for l in lines if "fetch" in l or "Parallel" in l or "road_flows" in l]
print(f"Found {len(road_logs)} matching lines. Last 20 matching lines:")
for rl in road_logs[-20:]:
    print(rl)
