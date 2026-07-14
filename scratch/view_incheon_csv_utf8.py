import pandas as pd
import os

path = r"c:\Users\llll\Documents\두인경매\바이브코딩\data\인천재개발추진현황_20260430.csv"
out_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\incheon_utf8.txt"

if not os.path.exists(path):
    print("CSV not found!")
    exit(1)

try:
    df = pd.read_csv(path, encoding='cp949')
    print("Columns:", df.columns.tolist())
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"Total Rows: {len(df)}\n")
        f.write(f"Columns: {df.columns.tolist()}\n\n")
        for idx, row in df.iterrows():
            f.write(f"Row {idx}: {row.to_dict()}\n")
            
    print("Successfully wrote UTF-8 output to", out_path)
except Exception as e:
    print("Error:", e)
