import pandas as pd
import os
import glob

realprice_dir = r"c:\Users\llll\Documents\두인경매\바이브코딩\realprice"
csv_files = glob.glob(os.path.join(realprice_dir, "*.csv"))

if csv_files:
    # Read the first CSV file to inspect columns
    file_path = csv_files[0]
    print(f"Inspecting file: {os.path.basename(file_path)}")
    try:
        df = pd.read_csv(file_path, nrows=5)
        print("Columns:")
        print(df.columns.tolist())
        print("\nFirst row:")
        print(df.iloc[0].to_dict())
    except Exception as e:
        print(f"Error reading CSV directly: {e}")
        print("Trying with encoding='cp949' or 'utf-8'...")
        for encoding in ['cp949', 'utf-8-sig', 'utf-8', 'latin1']:
            try:
                df = pd.read_csv(file_path, encoding=encoding, nrows=5)
                print(f"Success with encoding: {encoding}")
                print("Columns:")
                print(df.columns.tolist())
                print("\nFirst row:")
                print(df.iloc[0].to_dict())
                break
            except Exception as ex:
                print(f"Failed with {encoding}: {ex}")
else:
    print("No CSV files found in realprice folder.")
