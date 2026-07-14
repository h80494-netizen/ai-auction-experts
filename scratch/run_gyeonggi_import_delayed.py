import time
import subprocess
import os

print("Waiting 70 seconds for Incheon import task to complete and avoid Nominatim rate-limiting...")
time.sleep(70)

print("\nStarting Gyeonggi Redevelopment import...")
script_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\import_gyeonggi_redevelopment.py"

if os.path.exists(script_path):
    # Run the Gyeonggi import script
    res = subprocess.run(["python", script_path], capture_output=True, text=True)
    print("Return code:", res.returncode)
    print("Stdout:")
    print(res.stdout)
    print("Stderr:")
    print(res.stderr)
else:
    print("Gyeonggi import script not found!")
