import subprocess
try:
    res = subprocess.run(["git", "status"], capture_output=True, text=True, shell=True)
    print("STATUS:")
    print(res.stdout)
    print(res.stderr)
    res2 = subprocess.run(["git", "diff", "public/map.html"], capture_output=True, text=True, shell=True)
    with open("c:/Users/llll/Documents/두인경매/바이브코딩/scratch/git_diff.txt", "w", encoding="utf-8") as f:
        f.write(res2.stdout)
    print("DIFF WRITTEN")
except Exception as e:
    print("ERROR:", e)
