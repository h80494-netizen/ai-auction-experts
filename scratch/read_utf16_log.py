import os

log_file = 'backend/server_run.log'
if os.path.exists(log_file):
    print("Content of backend/server_run.log:")
    with open(log_file, 'r', encoding='utf-16') as f:
        print(f.read())
else:
    print("Log file not found.")
