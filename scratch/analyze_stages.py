import pandas as pd
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')

# Read excel
df = pd.read_excel('seoul_projects.xls', engine='xlrd')

# The first row seems to be the header
df.columns = df.iloc[0]
df = df[1:].reset_index(drop=True)

# Print columns to see the exact names
print("Columns:", df.columns.tolist())

# Print unique values of the progress stage column
stage_col = [c for c in df.columns if '진행단계' in str(c) or '단계' in str(c)]
if stage_col:
    print("\nUnique stages in column:", stage_col[0])
    print(df[stage_col[0]].unique())
else:
    print("\nCould not find stage column. Here are the first few rows:")
    print(df.head())
