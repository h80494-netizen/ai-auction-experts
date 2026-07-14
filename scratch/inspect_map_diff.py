import subprocess

res = subprocess.run(["git", "diff", "public/map.html"], capture_output=True, text=True, encoding="utf-8")
diff_text = res.stdout

with open("scratch/map_diff.txt", "w", encoding="utf-8") as f:
    f.write(diff_text)

print("SUCCESS: Written git diff of public/map.html to scratch/map_diff.txt")
