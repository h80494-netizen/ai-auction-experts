import subprocess

output_file = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\git_log.txt"

res = subprocess.run(["git", "log", "--oneline", "-n", "30"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(res.stdout)

print("Done! Git log written.")
