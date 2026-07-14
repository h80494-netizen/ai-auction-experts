import pandas as pd
import json

xls = pd.ExcelFile('data/지하철역사.xlsx')
print("Sheets:", xls.sheet_names)

for sheet in xls.sheet_names:
    print(f"\n--- Sheet: {sheet} ---")
    df = pd.read_excel('data/지하철역사.xlsx', sheet_name=sheet)
    print("Columns:", df.columns.tolist())
    print("Head:\n", df.head(3))
    
    # Check if there are specific columns like '노선', '지하철명', '주소', '위도', '경도', '상태' etc.
    # Print value counts of some key columns if they exist
    for col in df.columns:
        unique_vals = df[col].dropna().unique()
        print(f"Column '{col}' unique values count: {len(unique_vals)}")
        if len(unique_vals) < 20:
            print(f"  Values: {list(unique_vals)[:20]}")
        else:
            print(f"  Sample values: {list(unique_vals)[:5]}")
