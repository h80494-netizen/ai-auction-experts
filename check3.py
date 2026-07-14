import pandas as pd

df = pd.read_excel('data/경공매데이터_260515.xlsx', header=0, nrows=5)
if '사건번호' not in df.columns:
    df = pd.read_excel('data/경공매데이터_260515.xlsx', header=1, nrows=5)
if '사건번호' not in df.columns:
    df = pd.read_excel('data/경공매데이터_260515.xlsx', header=2, nrows=5)

with open('columns_utf8.txt', 'w', encoding='utf-8') as f:
    for c in df.columns:
        f.write(f"{c}\n")

row_dict = df.iloc[0].fillna('').to_dict()
with open('row_utf8.txt', 'w', encoding='utf-8') as f:
    for k, v in row_dict.items():
        f.write(f"{k}: {v}\n")
