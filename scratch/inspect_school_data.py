import pandas as pd
import os
import sys

# Force output to use utf-8
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

data_dir = "data"

school_path = os.path.join(data_dir, "중학교학군.xlsx")
subway_path = os.path.join(data_dir, "지하철역사.xlsx")
rate_path = os.path.join(data_dir, "특목고진학률.xlsx")

print("=== 중학교학군.xlsx ===")
if os.path.exists(school_path):
    xl = pd.ExcelFile(school_path)
    print("Sheets:", xl.sheet_names)
    for sheet in xl.sheet_names:
        df = pd.read_excel(school_path, sheet_name=sheet)
        print(f"\nSheet '{sheet}' head (rows: {len(df)}):")
        print("Columns:", df.columns.tolist())
        for idx, row in df.head(10).iterrows():
            print(f"Row {idx}: {row.tolist()}")
else:
    print("중학교학군.xlsx not found")

print("\n=== 특목고진학률.xlsx ===")
if os.path.exists(rate_path):
    xl = pd.ExcelFile(rate_path)
    print("Sheets:", xl.sheet_names)
    for sheet in xl.sheet_names:
        df = pd.read_excel(rate_path, sheet_name=sheet)
        print(f"\nSheet '{sheet}' head (rows: {len(df)}):")
        print("Columns:", df.columns.tolist())
        for idx, row in df.head(10).iterrows():
            print(f"Row {idx}: {row.tolist()}")
else:
    print("특목고진학률.xlsx not found")

print("\n=== 지하철역사.xlsx ===")
if os.path.exists(subway_path):
    xl = pd.ExcelFile(subway_path)
    print("Sheets:", xl.sheet_names)
    for sheet in xl.sheet_names:
        df = pd.read_excel(subway_path, sheet_name=sheet)
        print(f"\nSheet '{sheet}' head (rows: {len(df)}):")
        print("Columns:", df.columns.tolist())
        for idx, row in df.head(10).iterrows():
            print(f"Row {idx}: {row.tolist()}")
else:
    print("지하철역사.xlsx not found")
