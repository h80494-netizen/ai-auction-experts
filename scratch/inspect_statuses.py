import pandas as pd
excel_path = "data/지하철역1(위례과천선포함).xlsx"
df1 = pd.read_excel(excel_path, sheet_name='전국_노선망_종합분석', header=1)
df1.columns = [str(c).strip() for c in df1.columns]
print("Unique status values in Sheet 1:")
print(df1['현재 상황 및 검증 결과'].value_counts())
