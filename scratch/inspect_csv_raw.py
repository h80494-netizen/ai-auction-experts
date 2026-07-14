import os
import glob

realprice_dir = r"c:\Users\llll\Documents\두인경매\바이브코딩\realprice"
csv_files = glob.glob(os.path.join(realprice_dir, "*.csv"))

if csv_files:
    file_path = csv_files[0]
    print(f"Reading raw lines of file: {os.path.basename(file_path)}")
    try:
        with open(file_path, 'r', encoding='cp949') as f:
            for i in range(30):
                line = f.readline()
                if not line:
                    break
                print(f"Line {i+1}: {line.strip()}")
    except Exception as e:
        print(f"Error reading file raw: {e}")
else:
    print("No CSV files found.")
