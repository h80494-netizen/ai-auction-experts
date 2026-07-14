import pandas as pd
df = pd.read_excel('data/지하철역1(위례과천선포함).xlsx', sheet_name=0, header=1)
with open('scratch/status_unique.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(map(str, df.iloc[:,6].dropna().unique())))
