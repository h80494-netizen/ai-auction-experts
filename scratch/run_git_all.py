import subprocess

output_file = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\git_status.txt"

with open(output_file, "w", encoding="utf-8") as f:
    res = subprocess.run(["git", "branch", "-a"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
    f.write("=== BRANCHES ===\n" + res.stdout + "\n")
    
    res = subprocess.run(["git", "status"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
    f.write("=== STATUS ===\n" + res.stdout + "\n")
    
    res = subprocess.run(["git", "reflog", "-n", "50"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
    f.write("=== REFLOG ===\n" + res.stdout + "\n")

print("Done! Git status and branches written.")
