try:
    with open("c:/Users/llll/Documents/두인경매/바이브코딩/scratch/git_diff_clean.txt", "r", encoding="utf-8", errors="ignore") as f:
        diff_text = f.read()
    
    lines = diff_text.split("\n")
    print(f"Total diff lines: {len(lines)}")
    
    # Let's search for deleted lines that contain keywords
    keywords = ["용도지역", "도시계획", "계획도로", "재개발", "단계별", "도로종류", "도로종류별", "zoning", "planning", "dev1", "dev3", "stage", "class", "check"]
    
    print("\n--- DELETED LINES IN MAP.HTML WITH KEYWORDS ---")
    deleted_lines = []
    for line in lines:
        if line.startswith("-") and not line.startswith("---"):
            if any(k in line for k in keywords):
                deleted_lines.append(line)
                
    print(f"Total matching deleted lines: {len(deleted_lines)}")
    for dl in deleted_lines[:150]:
        print(dl)
        
except Exception as e:
    print("ERROR:", e)
