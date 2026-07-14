import pandas as pd
import re

df = pd.read_excel('data/명문중배정행정동.xlsx')
all_dongs = set()

for idx, row in df.iterrows():
    dong_str = str(row['해당동'])
    # 쉼표, 공백 등으로 분리
    parts = re.split(r'[,/\s]+', dong_str)
    for p in parts:
        p = p.strip()
        if p and p not in ['동구', '연수구', '일산동구', '일산서구', '분당구', '수지구', '과천시', '안양시']: # 시군구 제외
            # 숫자 뒤에 '통'이 들어간 특수 케이스 제외
            if '통' in p:
                continue
            all_dongs.add(p)

print(f"Total Unique Dongs ({len(all_dongs)}):")
print(sorted(list(all_dongs)))
