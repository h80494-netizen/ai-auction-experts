import subprocess

commits = ['7ab5e8b', '19715e8', '4fcdee2', 'cfca8b4']

for c in commits:
    print(f"=== Commits {c} ===")
    res = subprocess.run(["git", "show", f"{c}:public/map.html"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if res.returncode == 0:
        content = res.stdout
        # check if AND or OR highlighter was there
        if 'highlighter' in content:
            print("  Contains 'highlighter'")
            # find surrounding text of applyHighlighter
            idx = content.find("function applyHighlighter()")
            if idx != -1:
                print("  Found applyHighlighter() block:")
                print(content[idx : idx + 800])
            else:
                print("  applyHighlighter() not found in this commit!")
    else:
        print("  Could not read map.html in this commit")
