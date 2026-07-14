import pandas as pd
import numpy as np

# A series that contains '계약면적(㎡)' but not '전용면적(㎡)'
s = pd.Series({'계약면적(㎡)': '120.5', '지목': '대'})

# What does s.get('전용면적(㎡)', s.get('전용/연면적(㎡)', s.get('연면적(㎡)', s.get('계약면적(㎡)', 0.0)))) return?
val = s.get('전용면적(㎡)', s.get('전용/연면적(㎡)', s.get('연면적(㎡)', s.get('계약면적(㎡)', 0.0))))
print("Chained get result:", val)
print("Type of result:", type(val))

# What happens if we do:
# row.get('전용면적(㎡)', row.get('전용/연면적(㎡)', ...))
# If any column is present in the CSV file but its value in a specific row is NaN or empty?
# Let's test if there is '전용면적(㎡)' column but it is NaN
s2 = pd.Series({'전용면적(㎡)': np.nan, '계약면적(㎡)': '120.5'})
val2 = s2.get('전용면적(㎡)', s2.get('계약면적(㎡)', 0.0))
print("NaN present in first column get result:", val2)
