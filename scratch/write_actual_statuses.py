import pandas as pd
excel_path = "data/지하철역1(위례과천선포함).xlsx"
df1 = pd.read_excel(excel_path, sheet_name='전국_노선망_종합분석', header=2)
status_counts = df1.iloc[:, -1].value_counts()
with open("scratch/actual_statuses.txt", "w", encoding="utf-8") as f:
    f.write(status_counts.to_string())
print("Done writing actual_statuses.txt")
