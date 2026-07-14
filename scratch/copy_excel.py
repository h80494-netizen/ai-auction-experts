import shutil
import os

src = 'data/지하철역1(위례과천선포함).xlsx'
dst = 'data/지하철역사1(위례과천선포함).xlsx'

if os.path.exists(src):
    shutil.copy(src, dst)
    print(f"Copied {src} to {dst}")
else:
    print(f"Source file {src} not found!")
