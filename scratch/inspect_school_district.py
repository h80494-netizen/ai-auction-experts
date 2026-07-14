import pandas as pd
import sys

# Force output to use utf-8
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

school_path = "data/중학교학군.xlsx"
df = pd.read_excel(school_path)
print("Row count:", len(df))
print("First column unique values:")
print(df.iloc[:, 0].value_counts(dropna=False))

print("\nRows where first column is Gyeonggi/Incheon or not '서울':")
non_seoul = df[df.iloc[:, 0] != '서울']
for idx, row in non_seoul.iterrows():
    print(f"Row {idx}: {row.tolist()[:7]}")
