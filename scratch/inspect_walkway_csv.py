import pandas as pd

walk_path = 'data/서울시 자치구별 도보 네트워크 공간정보.csv'
print(f"Reading first 50000 rows from {walk_path}...")
df = pd.read_csv(walk_path, encoding='cp949', nrows=50000)

print("\nValue counts for '노드링크 유형':")
print(df['노드링크 유형'].value_counts())

# Filter for LINK
links = df[df['노드링크 유형'] == 'LINK']
print("\nValue counts for '링크 유형 코드' (for LINK rows):")
print(links['링크 유형 코드'].value_counts())

print("\nSample records for link type codes:")
for code in links['링크 유형 코드'].unique():
    sample = links[links['링크 유형 코드'] == code].head(1)
    if not sample.empty:
        print(f"Code {code}: {sample.iloc[0].to_dict()}")
