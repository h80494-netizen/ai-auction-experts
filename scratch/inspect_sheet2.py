import pandas as pd
excel_path = "data/지하철역1(위례과천선포함).xlsx"
df2 = pd.read_excel(excel_path, sheet_name='위례과천선_계획안')
print(df2.to_string())
