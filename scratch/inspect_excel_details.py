import pandas as pd

excel_path = "data/지하철역1(위례과천선포함).xlsx"
xl = pd.ExcelFile(excel_path)

with open("scratch/excel_structure.txt", "w", encoding="utf-8") as f:
    f.write(f"Sheet Names: {xl.sheet_names}\n")
    for sheet in xl.sheet_names:
        f.write(f"\n--- Sheet: {sheet} ---\n")
        df = pd.read_excel(excel_path, sheet_name=sheet)
        f.write(f"Columns: {df.columns.tolist()}\n")
        f.write(f"Shape: {df.shape}\n")
        f.write(f"First 10 rows:\n")
        f.write(df.head(10).to_string())
        f.write("\n")

print("Done! Structure written to scratch/excel_structure.txt")
