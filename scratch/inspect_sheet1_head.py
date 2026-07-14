import pandas as pd
excel_path = "data/지하철역1(위례과천선포함).xlsx"
df1 = pd.read_excel(excel_path, sheet_name='전국_노선망_종합분석')
for i in range(5):
    print(f"Row {i}: {df1.iloc[i].tolist()}")
