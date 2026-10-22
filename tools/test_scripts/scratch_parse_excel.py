import pandas as pd

try:
    df = pd.read_excel('data/지하철역1(위례과천선포함).xlsx', sheet_name=0)
    print("Columns:", list(df.columns))
    print(df.head(3).to_dict('records'))
except Exception as e:
    print("Error:", e)
