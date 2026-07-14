import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel('seoul_projects.xls', engine='xlrd')
df.columns = df.iloc[0]
df = df[1:].reset_index(drop=True)

# Search for Eunpyeong New Town or Jingwan-dong
eunpyeong = df[df['자치구'].astype(str).str.contains('은평')]
print(f"Eunpyeong-gu total projects: {len(eunpyeong)}")

jingwan = df[df['대표지번'].astype(str).str.contains('진관')]
print(f"Jingwan-dong projects: {len(jingwan)}")

eunpyeong_nt = df[df['사업장명'].astype(str).str.contains('은평뉴타운|은평 뉴타운')]
print(f"Projects containing '은평뉴타운': {len(eunpyeong_nt)}")

if len(jingwan) > 0:
    print("\nJingwan-dong projects:")
    print(jingwan[['사업장명', '진행단계', '사업구분', '대표지번']])

if len(eunpyeong_nt) > 0:
    print("\n'Eunpyeong New Town' projects:")
    print(eunpyeong_nt[['사업장명', '진행단계', '사업구분', '대표지번']])

# Categorization rules
early = ['안전진단', '정비계획 수립', '정비구역지정', '추진위원회승인', '추진위구성', '조합규약작성', '조합원 모집신고', '조합창립총회', '지구단위계획수립/건축심의/교통심의']
middle = ['조합설립인가', '사업시행인가', '사업계획승인']
late = ['관리처분인가', '철거', '철거 및 착공', '착공', '분양', '준공인가', '이전고시', '조합해산', '청산 및 조합해산', '조합청산']

def categorize(stage):
    if pd.isna(stage):
        return '미분류'
    if stage in early:
        return '초기 (조합인가 이전)'
    elif stage in middle:
        return '중기 (관리처분인가 이전)'
    elif stage in late:
        return '후기 (관리처분인가 이후)'
    else:
        return '기타/미분류'

df['분류'] = df['진행단계'].apply(categorize)

print("\nCategory counts:")
print(df['분류'].value_counts())

# Save the classified data to a CSV for artifact creation if needed
df.to_csv('classified_projects.csv', index=False, encoding='utf-8-sig')
