encodings = ['utf-8', 'cp949', 'euc-kr', 'utf-16']
for enc in encodings:
    try:
        with open('public/map.html', 'r', encoding=enc) as f:
            content = f.read()
        print(f"Success with {enc}, length={len(content)}")
        # Check if there is "서울" in the content
        if "서울" in content:
            print(f" - '서울' found in {enc}!")
            # Print lines 910 to 930
            lines = content.split('\n')
            for idx in range(910, min(930, len(lines))):
                print(f"   {idx+1}: {lines[idx]}")
            break
    except Exception as e:
        print(f"Failed with {enc}: {e}")
