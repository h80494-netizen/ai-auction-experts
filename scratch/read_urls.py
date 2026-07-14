import pandas as pd

df = pd.read_excel(r'c:\Users\llll\Documents\두인경매\바이브코딩\data\지자체고시도메인.xlsx')
print(df.head(10))
print("Columns:", df.columns)
