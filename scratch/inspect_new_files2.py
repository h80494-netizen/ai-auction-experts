import pandas as pd
import os
import sys

# Set standard output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

data_dir = "data"

school_path = os.path.join(data_dir, "중학교학군.xlsx")
subway_path = os.path.join(data_dir, "지하철역사.xlsx")
rate_path = os.path.join(data_dir, "특목고진학률.xlsx")

print("--- 중학교학군.xlsx ---")
if os.path.exists(school_path):
    xl = pd.ExcelFile(school_path)
    print("Sheets:", xl.sheet_names)
    for sheet in xl.sheet_names:
        df = pd.read_excel(school_path, sheet_name=sheet)
        print(f"\nSheet '{sheet}' head (rows: {len(df)}):")
        print("Columns:", df.columns.tolist())
        # print first 5 rows, but format nicely
        for idx, row in df.head(5).iterrows():
            print(f"Row {idx}: {dict(row)}")

print("\n--- 지하철역사.xlsx ---")
if os.path.exists(subway_path):
    xl = pd.ExcelFile(subway_path)
    print("Sheets:", xl.sheet_names)
    for sheet in xl.sheet_names:
        df = pd.read_excel(subway_path, sheet_name=sheet)
        print(f"\nSheet '{sheet}' head (rows: {len(df)}):")
        print("Columns:", df.columns.tolist())
        for idx, row in df.head(5).iterrows():
            print(f"Row {idx}: {dict(row)}")

print("\n--- 특목고진학률.xlsx ---")
if os.path.exists(rate_path):
    xl = pd.ExcelFile(rate_path)
    print("Sheets:", xl.sheet_names)
    for sheet in xl.sheet_names:
        df = pd.read_excel(rate_path, sheet_name=sheet)
        print(f"\nSheet '{sheet}' head (rows: {len(df)}):")
        print("Columns:", df.columns.tolist())
        for idx, row in df.head(5).iterrows():
            print(f"Row {idx}: {dict(row)}")
