import pandas as pd
import json

df = pd.read_excel('data/명문중배정행정동.xlsx')
cols = list(df.columns)
print("Original Columns:", cols)

# Let's save a dict to JSON with utf-8
data = []
for idx, row in df.iterrows():
    data.append({
        "학군": str(row.iloc[0]),
        "해당동": str(row.iloc[1])
    })

with open('scratch/excel_utf8.json', 'w', encoding='utf-8') as f:
    json.dump({"columns": cols, "rows": data}, f, ensure_ascii=False, indent=2)

print("Saved scratch/excel_utf8.json")
