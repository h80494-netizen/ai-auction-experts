import os
import glob
import pandas as pd

REALPRICE_DIR = r"c:\Users\llll\Documents\두인경매\바이브코딩\realprice"
csv_files = glob.glob(os.path.join(REALPRICE_DIR, "*.csv"))

for f in csv_files:
    fname = os.path.basename(f)
    try:
        df = pd.read_csv(f, skiprows=15, nrows=2, encoding='cp949')
        df.columns = [c.strip() for c in df.columns]
        has_sgg = '시군구' in df.columns
        print(f"File: {fname} | Has '시군구': {has_sgg}")
        if not has_sgg:
            # print first 5 columns
            print("  First 5 columns:", list(df.columns)[:5])
    except Exception as e:
        print(f"File: {fname} | Error: {e}")
