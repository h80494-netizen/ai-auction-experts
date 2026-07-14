import subprocess

output_file = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\git_diff_all.txt"

with open(output_file, "w", encoding="utf-8") as f:
    res = subprocess.run(["git", "log", "-p", "public/map.html"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
    f.write(res.stdout)

print("Done! Diff written.")
