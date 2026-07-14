import pandas as pd
import os

path = r"c:\Users\llll\Documents\두인경매\바이브코딩\data\인천재개발추진현황_20260430.csv"

if not os.path.exists(path):
    print("CSV not found!")
    exit(1)

# Check encoding and load first few rows
for enc in ['cp949', 'utf-8', 'euc-kr']:
    try:
        df = pd.read_csv(path, encoding=enc)
        print(f"Loaded successfully with {enc}!")
        cols = df.columns.tolist()
        print("Columns:", [repr(c) for c in cols])
        print("Shape:", df.shape)
        for idx, row in df.head(10).iterrows():
            print(f"Row {idx}:", {c: repr(row[c]) for c in cols})
        break
    except Exception as e:
        print(f"Failed with {enc}: {e}")
