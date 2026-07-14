import pandas as pd
import sys

df = pd.read_csv('data/road.csv', encoding='cp949')

with open('scratch/inspect_road_output_utf8.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total rows: {len(df)}\n")
    f.write(f"Columns: {list(df.columns)}\n\n")

    cols_to_inspect = ['present_sn', 'dgm_nm', 'grad_se', 'road_ty', 'lcl_nam', 'mls_nam', 'scl_nam', 'atr_nam', 'pmi_nam', 'dgm_lt', 'dgm_ar']
    f.write("Sample Data:\n")
    f.write(df[cols_to_inspect].head(20).to_string() + "\n\n")

    f.write("Value counts for grad_se:\n")
    f.write(df['grad_se'].value_counts(dropna=False).to_string() + "\n\n")

    f.write("Value counts for road_ty:\n")
    f.write(df['road_ty'].value_counts(dropna=False).to_string() + "\n\n")

    f.write("Value counts for scl_nam:\n")
    f.write(df['scl_nam'].value_counts(dropna=False).head(30).to_string() + "\n\n")

    f.write("Unique values of dgm_nm (first 50):\n")
    f.write(df['dgm_nm'].value_counts().head(50).to_string() + "\n\n")
