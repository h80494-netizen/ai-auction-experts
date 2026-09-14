import sys
import io
import pandas as pd
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sale_file = 'data/실거래가/부동산_실거래가_매매_분석_20260903_101751.xlsx'
rent_file = 'data/실거래가/부동산_실거래가_전월세_분석_20260903_101751.xlsx'

print("=== SALE FILE SHEETS ===")
xl_sale = pd.ExcelFile(sale_file)
for s in xl_sale.sheet_names:
    df = pd.read_excel(sale_file, sheet_name=s)
    types = df['시트용_유형'].dropna().unique().tolist() if '시트용_유형' in df.columns else []
    print(f"Sheet [{s}]: rows={len(df)}, types={types}, cols={df.columns.tolist()[:4]}")

print("\n=== RENT FILE SHEETS ===")
xl_rent = pd.ExcelFile(rent_file)
for s in xl_rent.sheet_names:
    df = pd.read_excel(rent_file, sheet_name=s)
    types = df['시트용_유형'].dropna().unique().tolist() if '시트용_유형' in df.columns else []
    print(f"Sheet [{s}]: rows={len(df)}, types={types}, cols={df.columns.tolist()[:4]}")
