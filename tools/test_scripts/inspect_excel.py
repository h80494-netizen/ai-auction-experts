import pandas as pd
import json
import os

file_path = "c:/Users/llll/Documents/두인경매/바이브코딩/data/GPS주소와 거리찾기_260504.xlsx"
print(f"Reading {file_path}...")

try:
    xl = pd.ExcelFile(file_path)
    print("Sheets found:", xl.sheet_names)
    
    summary = {}
    for sheet in xl.sheet_names:
        # Read just the first 5 rows to get headers and sample data
        df = pd.read_excel(file_path, sheet_name=sheet, nrows=5)
        
        # Convert columns to string list
        columns = df.columns.tolist()
        
        # Get up to 3 sample rows
        samples = df.head(3).fillna("").to_dict(orient="records")
        
        summary[sheet] = {
            "columns": columns,
            "samples": samples
        }
    
    with open("c:/Users/llll/Documents/두인경매/바이브코딩/data/gps_schema_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        
    print("Schema saved to data/gps_schema_summary.json")
    
except Exception as e:
    print("Error:", str(e))
