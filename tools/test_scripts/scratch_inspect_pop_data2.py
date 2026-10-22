import pandas as pd
import glob
import os

files = glob.glob('data/500격자주거직장인구/*.csv')
for f in files[:2]:
    print(f"\nFile: {os.path.basename(f)}")
    df = pd.read_csv(f, encoding='cp949', header=None, nrows=5)
    print(df)
