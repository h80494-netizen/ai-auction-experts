import pandas as pd
import os

file_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\data\경공매데이터_update.xlsx"
print(f"Reading file: {file_path}")

try:
    df = pd.read_excel(file_path)
    
    if "특이사항" in df.columns:
        original_count = len(df)
        
        # Count how many are exactly 0, '0', or 0.0
        mask = df["특이사항"].astype(str).str.strip().isin(['0', '0.0'])
        count = mask.sum()
        
        # Replace
        df.loc[mask, "특이사항"] = "대항력 없음"
        
        print(f"Updated {count} rows where 특이사항 was 0.")
        
        # Save back to a new excel file
        new_file_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\data\경공매데이터_update_대항력.xlsx"
        df.to_excel(new_file_path, index=False)
        print(f"File saved successfully to {new_file_path}")
    else:
        print("Column '특이사항' not found in the file. Columns are:", df.columns.tolist())
except Exception as e:
    print(f"Error: {e}")
