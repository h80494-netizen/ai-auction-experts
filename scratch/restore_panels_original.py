import subprocess
import re

try:
    # Let's show public/map.html at each of the 4 commits in git
    res = subprocess.run(["git", "log", "--pretty=format:%H"], capture_output=True, text=True, shell=True)
    commits = res.stdout.strip().split("\n")
    print("Commits:", commits)
    
    for c in commits:
        res_show = subprocess.run(["git", "show", f"{c}:public/map.html"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
        content = res_show.stdout
        
        # Look for the left-panel container
        match = re.search(r'<!-- Left Panel: Layer List -->.*?<!-- Right Panel: Filters -->', content, re.DOTALL)
        if match:
            print(f"\n--- LEFT PANEL IN COMMIT {c} ---")
            panel_html = match.group(0)
            print(f"Length: {len(panel_html)} characters")
            # Write to a file to inspect
            with open(f"c:/Users/llll/Documents/두인경매/바이브코딩/scratch/left_panel_{c[:8]}.html", "w", encoding="utf-8") as f:
                f.write(panel_html)
            
            # Print keywords occurrences in this panel
            for kw in ["용도지역", "도시계획도로", "계획도로", "재개발", "단계별", "도로종류", "도로종류별", "zoning", "planning-road"]:
                occ = len(re.findall(kw, panel_html))
                print(f"  Keyword '{kw}': {occ} times")
        else:
            print(f"Left panel not matched in commit {c}")
            
except Exception as e:
    print("ERROR:", e)
