import pandas as pd
import json
import os

files = {
    "bus": "data/경기버스정류소현황.xls",
    "pop": "data/경기유동인구_행정동단위집계.xls"
}

info = {}
for key, filepath in files.items():
    if os.path.exists(filepath):
        print(f"Reading {filepath}...")
        try:
            xls = pd.ExcelFile(filepath)
            sheet = xls.sheet_names[0]
            df = pd.read_excel(filepath, sheet_name=sheet)
            info[key] = {
                "sheets": xls.sheet_names,
                "columns": df.columns.tolist(),
                "shape": df.shape,
                "head": df.head(3).to_dict(orient='records')
            }
        except Exception as e:
            info[key] = {"error": str(e)}
    else:
        info[key] = {"error": "File not found"}

with open("scratch/new_data_schema.json", "w", encoding="utf-8") as f:
    json.dump(info, f, ensure_ascii=False, indent=2)

print("Saved schema to JSON!")
