import openpyxl
import os

files = [
    r"c:\Users\llll\Documents\두인경매\바이브코딩\data\GPS주소와 거리찾기_260504.xlsx",
    r"c:\Users\llll\Documents\두인경매\바이브코딩\data\경공매데이터_260515.xlsx"
]

for f in files:
    if not os.path.exists(f):
        print(f"File not found: {f}")
        continue
    print(f"\n=========================================")
    print(f"File: {f}")
    print(f"=========================================")
    try:
        wb = openpyxl.load_workbook(f, read_only=True)
        print("Sheets:", wb.sheetnames)
    except Exception as e:
        print("Error reading sheets:", e)
