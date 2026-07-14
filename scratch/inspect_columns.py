import pandas as pd
import os

EXCEL_PATH = os.path.join(os.path.dirname(__file__), '../data/경공매데이터_260515.xlsx')

print(f"Reading {EXCEL_PATH}...")
df = pd.read_excel(EXCEL_PATH, header=0) 
if '사건번호' not in df.columns:
    df = pd.read_excel(EXCEL_PATH, header=1)
if '사건번호' not in df.columns:
    df = pd.read_excel(EXCEL_PATH, header=2)

print("Actual Columns found:")
for idx, col in enumerate(df.columns):
    print(f"[{idx}] {col}")

print("\nFirst row sample values:")
for idx, col in enumerate(df.columns):
    val = df.iloc[0].get(col)
    print(f" - {col}: {val}")
