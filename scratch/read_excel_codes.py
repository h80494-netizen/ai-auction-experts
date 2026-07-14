import pandas as pd

file_path = 'data/도보네트워크_링크노드유형코드.xlsx'
df = pd.read_excel(file_path)
print("Columns in Excel:", df.columns)
print("\nFirst 30 rows of Excel:")
print(df.head(30).to_string())
