import os

log_files = ['backend/server.log', 'server.log']
for log_file in log_files:
    if os.path.exists(log_file):
        print(f"\n--- Logs in {log_file} (Last 100 lines) ---")
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        for line in lines[-150:]:
            if 'road_flows' in line or 'road' in line or 'fallback' in line or 'Overpass' in line or 'Failed' in line:
                print(line.strip())
