import pandas as pd
import re
import sys

# Force output to use utf-8
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 1. Load rates
rate_path = "data/특목고진학률.xlsx"
df_rates = pd.read_excel(rate_path, sheet_name="특목고학군")

# Clean column headers
df_rates.columns = [str(c).strip() for c in df_rates.columns]
# Row 0 contains exact headers: ['학교명', '주소', '과고', '외고/국제고', '자사고', '기타영재고', '총인원', '특목총계', '비율', '주소1', '지역', '지역1', '학군']
# Let's verify by setting the columns to Row 0 values
headers = df_rates.iloc[0].tolist()
df_rates = df_rates[1:]
df_rates.columns = headers
print("Rates Columns:", df_rates.columns.tolist())

# Convert '비율' to float and filter >= 0.30
df_rates['비율'] = pd.to_numeric(df_rates['비율'], errors='coerce')
elite_schools = df_rates[df_rates['비율'] >= 0.30]
print(f"Number of Elite Middle Schools (rate >= 30%): {len(elite_schools)}")

# List the elite schools
for idx, row in elite_schools.head(20).iterrows():
    print(f"- {row['학교명']}: {row['비율']:.4f} (Address: {row['주소']})")
