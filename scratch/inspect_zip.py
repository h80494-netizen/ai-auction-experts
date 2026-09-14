import sys
import io
import zipfile
import xml.etree.ElementTree as ET
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sale_0903 = 'data/실거래가/부동산_실거래가_매매_분석_20260903_101751.xlsx'

with zipfile.ZipFile(sale_0903, 'r') as z:
    print("Files in xlsx:")
    for f in z.infolist():
        if f.filename.startswith('xl/worksheets/'):
            print(f"  {f.filename}: size={f.file_size/1024/1024:.2f} MB")
            
    # Read sheet1.xml (종합매매) and sheet8.xml (아파트매매_1 or similar)
    # Get sheet names mapping from workbook.xml
    wb_xml = ET.fromstring(z.read('xl/workbook.xml'))
    sheets = wb_xml.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')
    for s in sheets:
        name = s.attrib['name']
        rId = s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
        print(f"Sheet name: {name} -> rId: {rId}")
