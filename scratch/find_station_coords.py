import pandas as pd

excel_path = "data/지하철역1(위례과천선포함).xlsx"
df1 = pd.read_excel(excel_path, sheet_name='전국_노선망_종합분석')
# Clean columns
df1.columns = [str(c).strip() for c in df1.columns]
# Find rows where header is row 1
header_row = 1
df1.columns = [str(x).strip() for x in df1.iloc[header_row]]
df1 = df1.iloc[header_row+1:].reset_index(drop=True)

search_names = ["정부과천청사", "양재시민의숲", "구룡", "도곡", "수서", "복정", "위례중앙"]

print("--- Matches in Sheet 1 ---")
for name in search_names:
    matches = df1[df1["지하철명(역명)"].str.contains(name, na=False)]
    print(f"\nSearch for: {name}")
    if not matches.empty:
        for idx, row in matches.iterrows():
            print(f"Line: {row['노선명']}, Name: {row['지하철명(역명)']}, Lat: {row['위도']}, Lng: {row['경도']}, Status: {row['현재 상황 및 검증 결과']}")
    else:
        print("No matches")
