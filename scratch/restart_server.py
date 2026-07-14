import subprocess
import os
import time
import urllib.request
import json

# 1. Find PID listening on 8000
pid = None
try:
    output = subprocess.check_output("netstat -ano | findstr :8000", shell=True).decode('cp949', errors='ignore')
    for line in output.strip().splitlines():
        if "LISTENING" in line:
            parts = line.split()
            pid = parts[-1]
            break
except Exception as e:
    print("Error checking port 8000:", e)

if pid:
    print(f"Found process {pid} listening on port 8000. Killing it...")
    try:
        subprocess.check_call(f"taskkill /F /PID {pid}", shell=True)
        print(f"Successfully killed process {pid}.")
    except Exception as e:
        print(f"Failed to kill process {pid}:", e)
else:
    print("No process found listening on port 8000.")

# 2. Wait a bit for the port to clear
time.sleep(1)

# 3. Start the backend server
print("Starting backend server...")
backend_dir = os.path.abspath("backend")
log_path = os.path.join(backend_dir, "backend.log")

# Start app.py in backend dir
try:
    with open(log_path, "w", encoding="utf-8") as log_file:
        proc = subprocess.Popen(
            ["python", "app.py"],
            cwd=backend_dir,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    print(f"Started backend server process with PID {proc.pid}. Logs redirected to backend/backend.log.")
except Exception as e:
    print("Failed to start backend server:", e)

# 4. Wait 3 seconds and verify
time.sleep(3)
url = "http://localhost:8000/api/map/road_flows?min_lat=37.48&max_lat=37.51&min_lng=127.01&max_lng=127.04"
try:
    print(f"Querying {url} to verify...")
    response = urllib.request.urlopen(url, timeout=5)
    data = json.loads(response.read().decode('utf-8'))
    print("Response status:", data.get('status'))
    features_count = len(data.get('data', {}).get('features', []))
    print("Features count:", features_count)
except Exception as e:
    print("Verification failed:", e)
