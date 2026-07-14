import pandas as pd
import sys

# Force output to use utf-8
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

subway_path = "data/지하철역사.xlsx"
df = pd.read_excel(subway_path, sheet_name="예정역포함")

print("Columns in 예정역포함:")
print(df.columns.tolist())

print("\nUnique values in 상황 column:")
print(df['상황'].value_counts(dropna=False))

# Show rows that are not '기존'
non_existing = df[df['상황'] != '기존']
print(f"\nNumber of non-existing (planned/new) stations: {len(non_existing)}")
for idx, row in non_existing.head(20).iterrows():
    print(f"Row {idx}: {row.tolist()}")
