import pandas as pd
excel_path = "data/지하철역1(위례과천선포함).xlsx"
df1 = pd.read_excel(excel_path, sheet_name='전국_노선망_종합분석', header=1)
print("Columns of Sheet 1:")
for idx, col in enumerate(df1.columns):
    print(f"Index {idx}: {repr(col)}")
print("\nUnique status values in last column:")
print(df1.iloc[:, -1].value_counts())
