import pandas as pd

file_path = 'data/도보네트워크_링크노드유형코드.xlsx'
df = pd.read_excel(file_path)

with open('scratch/excel_codes.txt', 'w', encoding='utf-8') as f:
    f.write("Columns: " + ", ".join(df.columns) + "\n\n")
    f.write(df.to_string())

print("Saved codes to scratch/excel_codes.txt")
