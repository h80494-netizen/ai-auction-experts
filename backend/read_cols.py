import pandas as pd
import glob
import os

try:
    files = glob.glob('../data/경공매데이터*.xlsx')
    if not files:
        print("No files found")
        exit(1)
    
    excel_file = files[0]
    print(f"Reading: {excel_file}")
    df = pd.read_excel(excel_file, header=2)
    cols = [c for c in df.columns if not str(c).startswith('Unnamed')]
    
    with open('excel_columns.txt', 'w', encoding='utf-8') as f:
        for c in cols:
            f.write(f"{c}\n")
    print("Columns written to excel_columns.txt")
except Exception as e:
    with open('excel_columns.txt', 'w', encoding='utf-8') as f:
        f.write(f"Error: {str(e)}\n")
