import pandas as pd
import sys

# Force output to use utf-8
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

rate_path = "data/특목고진학률.xlsx"
df = pd.read_excel(rate_path, sheet_name="특목고학군")

print("Columns:")
print(df.columns.tolist())

# The headers are in Row 0 based on our inspection, let's check
# Row 0: ['학교명', '주소', '과고', '외고/국제고', '자사고', '기타영재고', '총인원', '특목총계', '비율', '주소1', ...]
# So we should probably set header=1 or use the first row to rename columns.
# Let's inspect rows first.
for idx, row in df.head(5).iterrows():
    print(f"Row {idx}: {row.tolist()[:13]}")
