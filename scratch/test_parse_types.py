import os
import glob

REALPRICE_DIR = r"c:\Users\llll\Documents\두인경매\바이브코딩\realprice"
csv_files = glob.glob(os.path.join(REALPRICE_DIR, "*.csv"))

types = ['아파트', '연립다세대', '오피스텔', '단독다가구', '토지', '상업업무용', '공장창고등', '분양권']

for f in csv_files:
    name = os.path.basename(f)
    prop_type = '기타'
    for t in types:
        if t in name:
            prop_type = t
            break
    # Encode as ascii with escape sequence for non-ascii
    esc_name = name.encode('ascii', 'backslashreplace').decode('ascii')
    esc_match = prop_type.encode('ascii', 'backslashreplace').decode('ascii')
    print(f"File: {esc_name} -> Match: {esc_match}")
