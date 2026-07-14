import subprocess
try:
    res = subprocess.run(["git", "diff", "public/map.html"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
    lines = res.stdout.split("\n")
    print(f"Total diff lines: {len(lines)}")
    # Write entire diff to a file
    with open("c:/Users/llll/Documents/두인경매/바이브코딩/scratch/git_diff_clean.txt", "w", encoding="utf-8") as f:
        f.write(res.stdout)
    
    # Filter for deletions (-) and keyword matches
    print("Deleted lines containing keywords:")
    for line in lines:
        if line.startswith("-") and not line.startswith("---"):
            if any(k in line for k in ["개발", "단계", "도로", "택지", "구역", "버튼", "종류", "class"]):
                print(line)
except Exception as e:
    print("ERROR:", e)
