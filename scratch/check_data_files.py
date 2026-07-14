import os
import datetime

data_dir = "data"
for f in os.listdir(data_dir):
    path = os.path.join(data_dir, f)
    if os.path.isfile(path) and (f.endswith('.xlsx') or f.endswith('.xlsm') or f.endswith('.csv')):
        stat = os.stat(path)
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
        print(f"{f}: size={stat.st_size} bytes, mtime={mtime}")
