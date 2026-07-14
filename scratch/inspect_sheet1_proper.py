import pandas as pd
excel_path = "data/지하철역1(위례과천선포함).xlsx"
df1 = pd.read_excel(excel_path, sheet_name='전국_노선망_종합분석', header=2)
print("Columns with header=2:")
print(df1.columns.tolist())
print("\nFirst row with header=2:")
print(df1.iloc[0].tolist())
