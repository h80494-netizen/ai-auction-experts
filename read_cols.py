import pandas as pd
import json
df = pd.read_csv('data/수도권학원교습소정보_260515.csv', encoding='utf-8-sig', nrows=5)
with open('columns.json', 'w', encoding='utf-8') as f:
    json.dump(df.columns.tolist(), f, ensure_ascii=False)
