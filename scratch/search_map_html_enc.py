import sys

# Change console output encoding to utf-8 to avoid CP949 print errors
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

for enc in ['cp949', 'utf-8', 'euc-kr']:
    try:
        with open(r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html", "r", encoding=enc) as f:
            lines = f.readlines()
        print(f"\n--- Read successful with {enc} ---")
        for i, line in enumerate(lines):
            if "layers.dev" in line or "DGM_NM" in line:
                # print a few matching lines to check if Korean is correct
                if "재개발" in line or "구역" in line or "지구" in line or "도시" in line:
                    print(f"Line {i+1} ({enc}): {line.strip()}")
    except Exception as e:
        print(f"Failed to read with {enc}: {e}")
