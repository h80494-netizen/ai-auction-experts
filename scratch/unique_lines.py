import pandas as pd
import json

df = pd.read_excel('data/지하철역사.xlsx', '예정역포함')
lines = df['노선'].dropna().unique().tolist()

with open('scratch/unique_lines.json', 'w', encoding='utf-8') as f:
    json.dump(lines, f, ensure_ascii=False, indent=2)

print("Saved unique lines list to JSON!")
