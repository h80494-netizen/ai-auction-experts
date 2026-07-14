encodings = ['utf-8', 'cp949', 'euc-kr', 'utf-16']
for enc in encodings:
    try:
        with open('public/map.html', 'r', encoding=enc) as f:
            content = f.read()
        if "서울" in content:
            print(f"SUCCESS! '서울' found in cp949/euc-kr correctly!")
            # Print lines 910 to 930
            lines = content.split('\n')
            for idx in range(910, min(930, len(lines))):
                print(f"   {idx+1}: {lines[idx]}")
            print(f"Encoding is: {enc}")
            break
        else:
            # Let's search for some other common Korean word like "지하철" or "상권"
            if "상권" in content or "대시보드" in content:
                print(f"Found Korean in {enc}!")
                lines = content.split('\n')
                for idx in range(910, min(930, len(lines))):
                    print(f"   {idx+1}: {lines[idx]}")
                print(f"Encoding is: {enc}")
                break
    except Exception as e:
        print(f"Failed with {enc}: {e}")
