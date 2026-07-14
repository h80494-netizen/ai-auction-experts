import pandas as pd
df = pd.read_csv('data/road.csv', encoding='cp949', nrows=5)
print("road.csv columns:")
print(df.columns)
print("\nFirst 5 rows:")
print(df)
