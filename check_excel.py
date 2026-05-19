import pandas as pd
import glob

files = glob.glob('backend/data/*.xlsx')
print("Excel files:", files)
if files:
    df = pd.read_excel(files[0], header=2)
    print("최저가율 samples:", df['최저가율'].head(20).values.tolist())
    print("감정가 samples:", df['감정가(M)'].head(20).values.tolist())
    print("최저가 samples:", df['최저가(M)'].head(20).values.tolist())
