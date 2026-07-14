import os

log_paths = ['backend/server.log', 'server.log']

for path in log_paths:
    if os.path.exists(path):
        print(f"\n=== Last 50 lines of {path} ===")
        with open(path, 'rb') as f:
            try:
                f.seek(-10000, os.SEEK_END)
            except IOError:
                pass
            lines = f.read().decode('utf-8', errors='replace').splitlines()
            for line in lines[-50:]:
                print(line)
