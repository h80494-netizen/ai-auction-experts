import pandas as pd
excel_path = "data/지하철역1(위례과천선포함).xlsx"
xl = pd.ExcelFile(excel_path)
print("Sheet Names:", xl.sheet_names)
for sheet in xl.sheet_names:
    print(f"\n--- Sheet: {sheet} ---")
    df = pd.read_excel(excel_path, sheet_name=sheet)
    print("Columns:", df.columns.tolist())
    print("Shape:", df.shape)
    print("Head:\n", df.head(3))
