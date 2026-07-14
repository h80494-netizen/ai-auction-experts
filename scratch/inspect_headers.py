import os
import glob
import sys

# Ensure output is printed in utf-8
if sys.stdout.encoding != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

realprice_dir = r"c:\Users\llll\Documents\두인경매\바이브코딩\realprice"
csv_files = glob.glob(os.path.join(realprice_dir, "*.csv"))

if csv_files:
    # Let's inspect headers for several files
    for file_path in csv_files[:3]:
        print(f"\n--- Headers for: {os.path.basename(file_path)} ---")
        try:
            with open(file_path, 'r', encoding='cp949') as f:
                lines = f.readlines()
                # Find header line (it usually starts with "NO" or "번호")
                header_line = None
                for idx, line in enumerate(lines[:30]):
                    if line.startswith('"NO"') or line.startswith('NO'):
                        header_line = line.strip()
                        print(f"Found header at line {idx+1}: {header_line}")
                        # Print first data line
                        if idx + 1 < len(lines):
                            print(f"Data row: {lines[idx+1].strip()}")
                        break
        except Exception as e:
            print(f"Error: {e}")
else:
    print("No CSV files found.")
