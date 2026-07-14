import pandas as pd
import json

xls = pd.ExcelFile('data/지하철역사.xlsx')

info = {}
for sheet in xls.sheet_names:
    df = pd.read_excel('data/지하철역사.xlsx', sheet_name=sheet)
    info[sheet] = {
        "columns": df.columns.tolist(),
        "head": df.head(5).to_dict(orient='records'),
        "shape": df.shape
    }
    # check unique values of first sheet's '노선', '상태' or similar
    if sheet == xls.sheet_names[0]:
        info[sheet]["unique_cols"] = {}
        for col in df.columns:
            vals = df[col].dropna().unique().tolist()
            if len(vals) < 30:
                info[sheet]["unique_cols"][col] = vals
            else:
                info[sheet]["unique_cols"][col] = vals[:10]

with open("scratch/inspect_clean.json", "w", encoding="utf-8") as f:
    json.dump(info, f, ensure_ascii=False, indent=2)

print("JSON file saved!")
