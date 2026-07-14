import pandas as pd
import json

df = pd.read_excel('c:/Users/llll/Documents/두인경매/바이브코딩/data/아파트단지정보.xlsx', nrows=5)
columns = df.columns.tolist()

with open('c:/Users/llll/Documents/두인경매/바이브코딩/scratch/apt_cols.txt', 'w', encoding='utf-8') as f:
    for col in columns:
        f.write(str(col) + '\n')
    
    f.write("\n=== Sample Data ===\n")
    sample = df.head(1).to_dict('records')[0]
    for k, v in sample.items():
        f.write(f"{k}: {v}\n")
