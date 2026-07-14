import pandas as pd
import os

EXCEL_PATH = os.path.join(os.path.dirname(__file__), '../data/경공매데이터_260515.xlsx')

print(f"Reading {EXCEL_PATH}...")
df = pd.read_excel(EXCEL_PATH, header=0) 
if '사건번호' not in df.columns:
    df = pd.read_excel(EXCEL_PATH, header=1)
if '사건번호' not in df.columns:
    df = pd.read_excel(EXCEL_PATH, header=2)

print("Unique types in '입찰일':")
print(df['입찰일'].map(type).value_counts())

print("\nSample values of '입찰일':")
print(df['입찰일'].dropna().head(10))

for val in df['입찰일'].dropna().head(5):
    print(f"Value: {val}, Type: {type(val)}")
    try:
        dt = pd.to_datetime(val)
        print(f"  Parsed with to_datetime: {dt} (Formatted: {dt.strftime('%Y-%m-%d')})")
    except Exception as e:
        print(f"  to_datetime Error: {e}")
